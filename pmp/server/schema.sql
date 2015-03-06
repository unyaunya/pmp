drop table if exists entries;
create table users (
  id     string primary key,
  passwd string not null,
  email  string not null,
  name   string not null,
  apikey string not null,
  role   string not null
);
