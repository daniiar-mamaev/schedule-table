Commands to start application:

docker build -t schedule-table .

docker run -p 80:80 -e MONGO_DB_PASSWORD="will be sent by email" schedule-table
