CREATE TABLE user_data (
	id serial PRIMARY KEY,
	username varchar(255) UNIQUE NOT NULL,
	password char(60) NOT NULL,
	reg_date timestamp without time zone NOT NULL,
	reputation integer DEFAULT 0	
);

ALTER TABLE answer
ADD COLUMN user_id integer REFERENCES user_data(id);

ALTER TABLE question
ADD COLUMN user_id integer REFERENCES user_data(id),
ADD COLUMN accepted_answer_id integer REFERENCES answer(id);

ALTER TABLE comment
ADD COLUMN user_id integer REFERENCES user_data(id);

