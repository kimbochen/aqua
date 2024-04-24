image:
	docker build -t experimental .

attach:
	docker attach $(shell docker ps -aqf "ancestor=experimental")
