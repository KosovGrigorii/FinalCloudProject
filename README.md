# CloudProject
## Деплой к себе в облако

```
yc config profile get <имя проифиля>
export FOLDER_ID=<folder-id>
```

- В provider.tf кладем свой токен, folder-id, cloud-id (всё в кавычках)
```
cd deploy
```
- Включаем vpn
```
terraform init
```

- база данных:
```
terraform apply -target=yandex_ydb_database_serverless.movies_database
export DOCUMENT_API_ENDPOINT=<movies_database_document_api_endpoint>
export MOVIES_DATABASE_PATH=<movies_database_path>
```

- создание сервисного аккаунта:
```
terraform apply -target=yandex_iam_service_account.movies_api_sa
export MOVIES_API_SA_ID=<movies_api_sa_id>
terraform apply -target=yandex_iam_service_account_static_access_key.movies_api_sa_static_key
export AWS_ACCESS_KEY_ID=<access_key>
terraform output -raw private_key
export AWS_SECRET_ACCESS_KEY=< private_key>
```

- выдача права аккаунту:
```
yc resource-manager folder add-access-binding ${FOLDER_ID} --role ydb.admin --subject serviceAccount:${MOVIES_API_SA_ID}
yc resource-manager folder add-access-binding ${FOLDER_ID} --role container-registry.images.puller --subject serviceAccount:${MOVIES_API_SA_ID}
yc resource-manager folder add-access-binding ${FOLDER_ID} --role serverless.containers.invoker --subject serviceAccount:${MOVIES_API_SA_ID}
yc resource-manager folder add-access-binding ${FOLDER_ID} --role serverless.functions.invoker --subject serviceAccount:${MOVIES_API_SA_ID}
yc resource-manager folder add-access-binding ${FOLDER_ID} --role storage.editor --subject serviceAccount:${MOVIES_API_SA_ID}
yc resource-manager folder add-access-binding ${FOLDER_ID} --role yds.admin --subject serviceAccount:${MOVIES_API_SA_ID}
```

- Прописываем в backend/openapi.yaml и deploy/frontend_openapi.yaml наш MOVIES_API_SA_ID

- создание реестра и репозитория докер образов:
```
terraform apply -target=yandex_container_registry.default
terraform apply -target=yandex_container_repository.movies_api_repository
export MOVIES_API_REPOSITORY_NAME=<movies_api_repository_name>
```

- добавляем докер образ бекенда в реестр:
```
yc container registry configure-docker
cd backend
export APP_VERSION=1
docker build -t ${MOVIES_API_REPOSITORY_NAME}:0.0.1 .
docker push ${MOVIES_API_REPOSITORY_NAME}:0.0.1
cd deploy
```

- создаем serverless container, он будет запускаться из созданного образа:
```
yc sls container create --name movies-api-container --folder-id ${FOLDER_ID}
export MOVIES_API_CONTAINER_ID=<идентификатор контейнера>
yc sls container revisions deploy --folder-id ${FOLDER_ID} \
--container-id ${MOVIES_API_CONTAINER_ID} \
--memory 512M \
--cores 1 \
--execution-timeout 5s \
--concurrency 4 \
--environment AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID},AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY},DOCUMENT_API_ENDPOINT=${DOCUMENT_API_ENDPOINT},APP_VERSION=1 \
--service-account-id ${MOVIES_API_SA_ID} \
--image ${MOVIES_API_REPOSITORY_NAME}:0.0.1
```

- в backend/openapi.yaml заменяем ${MOVIES_API_CONTAINER_ID}
- делаем gateway для бека:
```
terraform apply -target=yandex_api_gateway.movies_api_gateway
export MOVIES_API_GATEWAY_DOMAIN=<movies_api_gateway_domain>
```

- Кладем MOVIES_API_GATEWAY_DOMAIN в frontend/Home.html
- проверяем работоспособность шлюза
```
 curl “${MOVIES_API_GATEWAY_DOMAIN}/movies"
 ```
Вывод: {“Items”:[]}
- создаем бакет для фронтена:
```
terraform apply -target=yandex_storage_bucket.movies_website_bucket
export MOVIES_WEBSITE_BUCKET=<movies_website_bucket>
```
- в deploy/frontend_openapi.yaml подставляем все наши значения
- делаем шлюз для фронта:
```
terraform apply -target=yandex_api_gateway.movies_frontend_gateway
export MOVIES_WEBSITE_GATEWAY_DOMAIN=<movies_website_gateway_domain>
```
Загружаем фронт в бакет:
```
aws --endpoint-url=https://storage.yandexcloud.net s3 cp --recursive ../frontend/ s3://${MOVIES_WEBSITE_BUCKET}
```


## Обновление версий фронтенда и бекенда
- заходим в ~/backend или ~/frontend
```
sh update.sh
```
**- При обновлении версии фронта значение может стать undefined, нужно подождать пару секунд и перезагрузить ui(я дико извиняюсь за этот непрофесионализм)**

**- Реплика меняется не каждый раз, а раз в какое-то время(сущность serverless container )**










