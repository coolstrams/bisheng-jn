from typing import Any, Dict

from bisheng.api.services.assistant_agent import AssistantAgent
from bisheng.api.services.llm import LLMService
from bisheng.chat.clients.llm_callback import LLMNodeCallbackHandler
from bisheng.database.models.knowledge import KnowledgeDao, Knowledge
from bisheng.interface.importing.utils import import_vectorstore
from bisheng.interface.initialize.loading import instantiate_vectorstore
from bisheng.utils.embedding import decide_embeddings
from bisheng.workflow.callback.event import StreamMsgOverData
from bisheng.workflow.nodes.base import BaseNode
from bisheng.workflow.nodes.prompt_template import PromptTemplateParser
from bisheng_langchain.gpts.assistant import ConfigurableAssistant
from bisheng_langchain.gpts.load_tools import load_tools
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from loguru import logger

agent_executor_dict = {
    'ReAct': 'get_react_agent_executor',
    'function call': 'get_openai_functions_agent_executor',
}


class AgentNode(BaseNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 判断是单次还是批量
        self._tab = self.node_data.tab['value']

        # 解析prompt
        self._system_prompt = PromptTemplateParser(template=self.node_params['system_prompt'])
        self._system_variables = self._system_prompt.extract()
        self._user_prompt = PromptTemplateParser(template=self.node_params['user_prompt'])
        self._user_variables = self._user_prompt.extract()

        self._batch_variable_list = {}
        self._system_prompt_list = []
        self._user_prompt_list = []
        self._tool_invoke_list = []

        # 聊天消息
        self._chat_history_flag = self.node_params['chat_history_flag']['value'] != 0
        self._chat_history_num = self.node_params['chat_history_flag']['value']

        self._llm = LLMService.get_bisheng_llm(model_id=self.node_params['model_id'],
                                               temperature=self.node_params.get(
                                                   'temperature', 0.3))

        # 是否输出结果给用户
        self._output_user = self.node_params.get('output_user', False)

        # tools
        self._tools = self.node_params['tool_list']

        # knowledge
        # self._knowledge_ids = self.node_params['knowledge_id']
        # 判断是知识库还是临时文件列表
        self._knowledge_type = self.node_params['knowledge_id']['type']
        self._knowledge_ids = [
            one['key'] for one in self.node_params['knowledge_id']['value']
        ]

        # 是否支持nl2sql
        self._sql_agent = self.node_params.get('sql_agent')
        self._sql_address = ''
        if self._sql_agent and self._sql_agent['open']:
            self._sql_address = f'mysql+pymysql://{self._sql_agent["db_username"]}:{self._sql_agent["db_password"]}@{self._sql_agent["db_address"]}/{self._sql_agent["db_name"]}?charset=utf8mb4'

        # agent
        self._agent_executor_type = 'get_react_agent_executor'
        self._agent = None

    def _init_agent(self, system_prompt: str):
        if self._agent:
            return
        # 获取配置的助手模型列表
        assistant_llm = LLMService.get_assistant_llm()
        if not assistant_llm.llm_list:
            raise Exception('助手推理模型列表为空')
        default_llm = [
            one for one in assistant_llm.llm_list if one.model_id == self.node_params['model_id']
        ]
        if not default_llm:
            raise Exception('选择的推理模型不在助手推理模型列表内')
        default_llm = default_llm[0]
        self._agent_executor_type = default_llm.agent_executor_type
        knowledge_retriever = {
            'max_content': default_llm.knowledge_max_content,
            'sort_by_source_and_index': default_llm.knowledge_sort_index
        }

        func_tools = self._init_tools()
        knowledge_tools = self._init_knowledge_tools(knowledge_retriever)
        sql_agent_tools = self.init_sql_agent_tool()
        func_tools.extend(knowledge_tools)
        func_tools.extend(sql_agent_tools)
        self._agent = ConfigurableAssistant(
            agent_executor_type=agent_executor_dict.get(self._agent_executor_type),
            tools=func_tools,
            llm=self._llm,
            assistant_message=system_prompt,
        )

    def _init_tools(self):
        if self._tools:
            tool_ids = [int(one['key']) for one in self._tools]
            return AssistantAgent.init_tools_by_toolid(tool_ids, self._llm, None)
        else:
            return []

    def init_sql_agent_tool(self):
        if not self._sql_address:
            return []
        tool_params = {
            'sql_agent': {
                'llm': self._llm,
                'sql_address': self._sql_address
            }
        }
        return load_tools(tool_params=tool_params, llm=self._llm)

    def _init_knowledge_tools(self, knowledge_retriever: dict):
        if not self._knowledge_ids:
            return []
        tools = []
        for index, knowledge_id in enumerate(self._knowledge_ids):
            if self._knowledge_type == 'knowledge':
                knowledge_info = KnowledgeDao.query_by_id(knowledge_id)
                name = f'knowledge_{knowledge_id}'
                description = f'{knowledge_info.name}:{knowledge_info.description}'
                vector_client = self.init_knowledge_milvus(knowledge_info)
                es_client = self.init_knowledge_es(knowledge_info)
            else:
                file_metadata = self.graph_state.get_variable_by_str(f'{knowledge_id}_file_metadata')
                if not file_metadata:
                    raise Exception(f'未找到对应的临时文件数据：{knowledge_id}')

                name = f'{knowledge_id.replace(".", "").replace("#", "")}_knowledge_{index}'
                description = f'{file_metadata.get("source")}:{file_metadata.get("title")}'

                vector_client = self.init_file_milvus(file_metadata)
                es_client = self.init_file_es(file_metadata)

            tool_params = {
                'bisheng_rag': {
                    'name': name,
                    'description': description,
                    'vector_store': vector_client,
                    'keyword_store': es_client,
                    'llm': self._llm,
                    **knowledge_retriever
                }
            }
            tools.extend(load_tools(tool_params=tool_params, llm=self._llm))

        return tools

    def init_knowledge_milvus(self, knowledge: Knowledge) -> 'Milvus':
        """ 初始化用户选择的知识库的milvus """
        params = {
            'collection_name': knowledge.collection_name,
            'embedding': decide_embeddings(knowledge.model)
        }
        if knowledge.collection_name.startswith('partition'):
            params['partition_key'] = knowledge.id
        return self._init_milvus(params)

    def init_file_milvus(self, file_metadata: Dict) -> 'Milvus':
        """ 初始化用户选择的临时文件的milvus """
        embeddings = LLMService.get_knowledge_default_embedding()
        if not embeddings:
            raise Exception('没有配置默认的embedding模型')
        file_ids = [file_metadata['file_id']]
        params = {
            'collection_name': self.tmp_collection_name,
            'partition_key': self.workflow_id,
            'embedding': embeddings,
            'metadata_expr': f'file_id in {file_ids}'
        }
        return self._init_milvus(params)

    @staticmethod
    def _init_milvus(params: dict):
        class_obj = import_vectorstore('Milvus')
        return instantiate_vectorstore('Milvus', class_object=class_obj, params=params)

    def init_knowledge_es(self, knowledge: Knowledge):
        params = {
            'index_name': knowledge.index_name
        }
        return self._init_es(params)

    def init_file_es(self, file_metadata: Dict):
        params = {
            'index_name': self.tmp_collection_name,
            'post_filter': {
                'terms': {
                    'metadata.file_id': [file_metadata['file_id']]
                }
            }
        }
        return self._init_es(params)

    @staticmethod
    def _init_es(params: Dict):
        class_obj = import_vectorstore('ElasticKeywordsSearch')
        return instantiate_vectorstore('ElasticKeywordsSearch', class_object=class_obj, params=params)

    def _run(self, unique_id: str):
        ret = {}
        variable_map = {}

        self._batch_variable_list = {}
        self._system_prompt_list = []
        self._user_prompt_list = []
        self._tool_invoke_list = []

        for one in self._system_variables:
            variable_map[one] = self.graph_state.get_variable_by_str(one)
        system_prompt = self._system_prompt.format(variable_map)
        self._system_prompt_list.append(system_prompt)
        self._init_agent(system_prompt)

        if self._tab == 'single':
            ret['output'] = self._run_once(None, unique_id, 'output')
            self.callback_manager.on_stream_over(StreamMsgOverData(node_id=self.id,
                                                                   msg=ret['output'],
                                                                   unique_id=unique_id,
                                                                   output_key='output'))
        else:
            for index, one in enumerate(self.node_params['batch_variable']):
                output_key = self.node_params['output'][index]['key']
                ret[output_key] = self._run_once(one, unique_id, output_key)
                self.callback_manager.on_stream_over(StreamMsgOverData(node_id=self.id,
                                                                       msg=ret[output_key],
                                                                       unique_id=unique_id,
                                                                       output_key=output_key))

        logger.debug('agent_over result={}', ret)
        if self._output_user:
            # 非stream 模式，处理结果
            for k, v in ret.items():
                answer = v
                self.graph_state.save_context(content=answer, msg_sender='AI')

        return ret

    def parse_log(self, unique_id: str, result: dict) -> Any:
        ret = []
        if self._batch_variable_list:
            ret.append({"key": "batch_variable", "value": self._batch_variable_list, "type": "params"})

        ret.extend([
            {"key": "system_prompt", "value": self._system_prompt_list, "type": "params"},
            {"key": "user_prompt", "value": self._user_prompt_list, "type": "params"},
        ])
        tool_invoke_info = {}
        if self._tool_invoke_list:
            for one in self._tool_invoke_list:
                if one['run_id'] not in tool_invoke_info:
                    tool_invoke_info[one['run_id']] = {}
                if one['type'] == 'start':
                    tool_invoke_info[one['run_id']].update({
                        'name': one['name'],
                        'input': one['input']
                    })
                elif one['type'] == 'end':
                    tool_invoke_info[one['run_id']].update({
                        'output': one['output']
                    })
                elif one['type'] == 'error':
                    tool_invoke_info[one['run_id']].update({
                        'output': f'Error: {one["error"]}'
                    })
        if tool_invoke_info:
            for one in tool_invoke_info.values():
                ret.append({
                    "key": one["name"],
                    "value": f"Tool Input:\n {one['input']}, Tool Output:\n {one['output']}",
                    "type": "tool"
                })
        ret.extend([{"key": f'{self.id}.{k}', "value": v, "type": "variable"} for k, v in result.items()])
        return ret

    def _run_once(self, input_variable: str = None, unique_id: str = None, output_key: str = None):
        """
        input_variable: 输入变量，如果是batch，则需要传入一个list，否则为None
        """
        # 说明是引用了批处理的变量, 需要把变量的值替换为用户选择的变量
        special_variable = f'{self.id}.batch_variable'
        variable_map = {}
        for one in self._system_variables:
            if input_variable and one == special_variable:
                variable_map[one] = self.graph_state.get_variable_by_str(input_variable)
                self._batch_variable_list[input_variable] = variable_map[one]
                continue
            variable_map[one] = self.graph_state.get_variable_by_str(one)
        # system = self._system_prompt.format(variable_map)

        variable_map = {}
        for one in self._user_variables:
            if input_variable and one == special_variable:
                variable_map[one] = self.graph_state.get_variable_by_str(input_variable)
                self._batch_variable_list[input_variable] = variable_map[one]
                continue
            variable_map[one] = self.graph_state.get_variable_by_str(one)
        user = self._user_prompt.format(variable_map)
        self._user_prompt_list.append(user)

        chat_history = []
        if self._chat_history_flag:
            chat_history = self.graph_state.get_history_list(self._chat_history_num)

        llm_callback = LLMNodeCallbackHandler(callback=self.callback_manager,
                                              unique_id=unique_id,
                                              node_id=self.id,
                                              output=self._output_user,
                                              output_key=output_key,
                                              tool_list=self._tool_invoke_list,
                                              cancel_llm_end=True)
        config = RunnableConfig(callbacks=[llm_callback])

        if self._agent_executor_type == 'ReAct':
            result = self._agent.invoke({
                'input': user,
                'chat_history': chat_history
            },
                config=config)
            output = result['agent_outcome'].return_values['output']
            if isinstance(output, dict):
                output = list(output.values())[0]
            return output
        else:
            chat_history.append(HumanMessage(content=user))
            result = self._agent.invoke(chat_history, config=config)
            return result[-1].content