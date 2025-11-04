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
  image: dataelement/bisheng-backend:v2.1.1

backend_worker:
  container_name: bisheng-backend-worker
  image: dataelement/bisheng-backend:v2.1.1

frontend:
  container_name: bisheng-frontend
  image: dataelement/bisheng-frontend:v2.1.1