script_path=./build/scripts
img_path=./build/Dockerfiles

include .env
export

build_local_images:
	docker buildx build -f ${img_path}/Dockerfile-odoo -t odoo .

create_network:
	docker network create odoo ||  echo ""

debug_odoo_image:
	make create_network
	docker run --entrypoint=/bin/bash -it \
	-p 8069:8069 --network odoo \
	--name odoo odoo

run_odoo: 
	make create_network
	docker run \
	-p 8069:8069 --network odoo \
	--name odoo -d odoo 

enter_odoo_container:	
	docker exec -it odoo bash

kill_odoo_container:
	docker rm odoo --force

debug_db:
	make create_network
	docker run --entrypoint=/bin/bash -it \
	-p 5432:5432 --network odoo \
	-e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	-e POSTGRES_USER=${POSTGRES_USER} \
	-e POSTGRES_DB=${POSTGRES_DB} \
	--name odoo_db postgres:17-bookworm

run_db: 
	make create_network
	docker run \
	-p 5432:5432 --network odoo \
	-e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	-e POSTGRES_USER=${POSTGRES_USER} \
	-e POSTGRES_DB=${POSTGRES_DB} \
	-v ./prev_data:/docker-entrypoint-initdb.d \
	--name odoo_db -d postgres:17-bookworm

enter_db_container:	
	docker exec -it odoo_db bash

kill_db_container:
	docker rm odoo_db --force

up:
	make run_db
	make run_odoo

kill: 
	make kill_db_container
	make kill_odoo_container

restart:
	make kill_db_container
	make kill_odoo_container
	make up