export $(cat .env | xargs)
make install && psql -a -d $DATABASE_URL -f database.sql