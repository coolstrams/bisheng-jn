升级到1.3.0
# 修改工具表中字段的数据类型
alter table bisheng.t_gpts_tools modify extra text default null;
alter table bisheng.t_gpts_tools_type modify extra text default null;

# 修改知识库文件表中字段的数据类型
alter table bisheng.knowledgefile modify split_rule text default null;



升级到2.0.0
# 插入联网搜索预置工具的配置
start transaction;
    INSERT INTO t_gpts_tools_type (name, logo, description, server_host, auth_method, api_key, auth_type, is_preset, user_id, is_delete) VALUES ('联网搜索', null, '搜索互联网信息，可配置使用不同的搜索引擎，目前支持 Bing、博查、Jina 深度搜索、SerpApi、Tavily。', null, null, '', null, 1, 1, 0);
    set @type_id=last_insert_id();
    INSERT INTO t_gpts_tools (name, logo, `desc`, api_params, tool_key, type, is_preset, is_delete, user_id) VALUES ('联网搜索', null, '使用 query 进行联网检索并返回结果。', '[{"in": "query", "name": "query", "schema": {"type": "string"}, "required": true, "description": "query to look up in Bing search"}]', 'web_search', @type_id, 1, 0, 1);
commit;

# 删除ft服务表中的索引
alter table server DROP index endpoint;
    
# 迁移工作台的embedding配置
start transaction;
set @embed_id=(select json_extract(cast(value as JSON), '$.embedding_model_id') from config where `key` = 'knowledge_llm');
insert into config (`key`, value) values ('linsight_llm', CONCAT('{"embedding_model": {"id": "', @embed_id, '"}}'));
commit;


升级到2.1.0
# 评测增加失败原因字段
alter table `evaluation` add column `description` varchar(255) null;

# 知识库文件表新增文件大小字段
alter table `knowledgefile` add column `file_size` bigint null; 

# 会话表新增应用的描述和logo字段
alter table `message_session` add column `flow_logo` varchar(255) null;
alter table `message_session` add column `flow_description` varchar(255) null;

修改docker-compose.yaml
# 修改backend和frontend的版本号为 2.1.0
backend:
  container_name: bisheng-backend
  image: dataelement/bisheng-backend:v2.1.0

backend_worker:
  container_name: bisheng-backend-worker
  image: dataelement/bisheng-backend:v2.1.0

frontend:
  container_name: bisheng-frontend
  image: dataelement/bisheng-frontend:v2.1.0
  
重启服务器
# 升级backend和frontend
docker-compose pull
docker-compose up -d