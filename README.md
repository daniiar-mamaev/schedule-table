Commands to start application:

docker build -t schedule-table .

docker run -p 80:80 -e MONGO_DB_PASSWORD=<i will send password in email> schedule-table
