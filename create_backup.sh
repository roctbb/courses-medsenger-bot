pg_dump -U postgres -W -d courses-medsenger-bot -h 127.0.0.1 > courses_bot.sql
zip -r courses.zip courses_bot.sql
