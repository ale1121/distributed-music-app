build:
	docker build backend -t muzo-web
	docker build streaming -t muzo-streaming

deploy:
	docker swarm init 2>/dev/null || true
	docker stack deploy -c stack.yml muzo

clean:
	docker stack rm muzo
