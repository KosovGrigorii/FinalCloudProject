#!/bin/bash

npm version patch;
aws s3api delete-objects --endpoint-url https://storage.yandexcloud.net --bucket ${MOVIES_WEBSITE_BUCKET} --delete "$(aws s3api list-object-versions --endpoint-url https://storage.yandexcloud.net --bucket ${MOVIES_WEBSITE_BUCKET} --query '{Objects: Versions[].{Key: Key, VersionId: VersionId}}' --max-items 1000)";
aws --endpoint-url=https://storage.yandexcloud.net s3 cp --recursive . s3://${MOVIES_WEBSITE_BUCKET};

