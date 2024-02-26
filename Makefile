develop : 
	 docker run -it -p 80:80 biasrecdocker bash

build : 
	docker build -t biasrecdocker .
