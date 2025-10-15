echo "--------------- Build du docker ---------------"
docker build -t projet .

echo "--------------- Run du docker ---------------"
    docker run -p 5007:5007 projet