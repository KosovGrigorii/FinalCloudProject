locals {
  frontend_gateway_name = "movies-frontend-gateway"
}

resource "yandex_api_gateway" "movies_frontend_gateway" {
  name      = local. frontend_gateway_name
  folder_id = local.folder_id
  spec      = file("../deploy/frontend_openapi.yaml")
}

output "movies_frontend_gateway_domain" {
  value = "https://${yandex_api_gateway.movies_frontend_gateway.domain}"
}