升级到2.0.0
     数据库变更
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

修改docker-compose.yaml
# 修改backend和frontend的版本号为 release
backend:
  container_name: bisheng-backend
  image: cr.dataelem.com/dataelement/bisheng-backend:v2.0.0

backend_worker:
  container_name: bisheng-backend-worker
  image: cr.dataelem.com/dataelement/bisheng-backend:v2.0.0

frontend:
  container_name: bisheng-frontend
  image: cr.dataelem.com/dataelement/bisheng-frontend:v2.0.0

修改启动脚本 bisheng/entrypoint.sh，使用以下内容覆盖
#!/bin/bash

export PYTHONPATH="./"

start_mode=${1:-api}

if [ $start_mode = "api" ]; then
    echo "Starting API server..."
    uvicorn bisheng.main:app --host 0.0.0.0 --port 7860 --no-access-log --workers 8
elif [ $start_mode = "worker" ]; then
    echo "Starting Celery worker..."
    # 处理知识库相关任务的worker
    nohup celery -A bisheng.worker.main worker -l info -c 20 -P threads -Q knowledge_celery -n knowledge@%h &
    # 工作流执行worker
    nohup celery -A bisheng.worker.main worker -l info -c 100 -P threads -Q workflow_celery -n workflow@%h &
    # 灵思任务的并发数，超出时会排队等待
    python bisheng/linsight/worker.py --worker_num 4 --max_concurrency 5
else
    echo "Invalid start mode. Use 'api' or 'worker'."
    exit 1
fi

重启服务器
# 升级backend和frontend
docker-compose pull
docker-compose up -d

# 灵思模块相关配置
linsight:
  # 历史记录中工具消息的最大token，超过后需要总结下历史记录
  tool_buffer: 100000
  # 单个任务最大执行步骤数，防止死循环
  max_steps: 200
  # 灵思任务执行过程中模型调用重试次数
  retry_num: 3
  # 灵思任务执行过程中模型调用重试间隔时间（秒）
  retry_sleep: 5
  # 生成SOP时，prompt里放的用户上传文件信息的数量
  max_file_num: 5
  # 生成SOP时，prompt里放的组织知识库的最大数量
  max_knowledge_num: 20

升级到2.0.3
修改nginx配置，nginx/conf.d/default.conf
# 其他部分不变，将minio转发的部分使用如下的配置替换
location ~ ^(/workspace)?/bisheng|/tmp-dir {
        rewrite ^/workspace(/.*)$ $1 break;
        proxy_pass http://minio:9000;
}

修改docker-compose.yaml
# 修改backend和frontend的版本号为 release
backend:
  container_name: bisheng-backend
  image: cr.dataelem.com/dataelement/bisheng-backend:v2.0.3

backend_worker:
  container_name: bisheng-backend-worker
  image: cr.dataelem.com/dataelement/bisheng-backend:v2.0.3

frontend:
  container_name: bisheng-frontend
  image: cr.dataelem.com/dataelement/bisheng-frontend:v2.0.3

重启服务器
# 升级backend和frontend
docker-compose pull
docker-compose up -d
