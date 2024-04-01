CREATE SCHEMA IF NOT EXISTS "public";

CREATE  TABLE "public".learning ( 
	user_id              integer  NOT NULL  ,
	word_id              integer  NOT NULL  ,
	correct_answers_number integer DEFAULT 0 NOT NULL  ,
	last_repeat          timestamp  NOT NULL  
 );

CREATE  TABLE "public".test ( 
	user_id              integer  NOT NULL  ,
	word_id              integer  NOT NULL  ,
	is_right             boolean    
 );

CREATE  TABLE "public".topics ( 
	title                varchar  NOT NULL  ,
	user_id              integer    ,
	id                   integer  NOT NULL GENERATED  ALWAYS AS IDENTITY ,
	description          varchar    ,
	CONSTRAINT pk_topics PRIMARY KEY ( id )
 );

CREATE  TABLE "public".users ( 
	last_repeat          timestamp    ,
	id                   integer  NOT NULL  ,
	topic_id             integer    ,
	questions_number     integer    ,
	correct_answers_number integer    ,
	"state"              integer DEFAULT 0 NOT NULL  ,
	is_reminder_send     boolean DEFAULT false   ,
	CONSTRAINT pk_users PRIMARY KEY ( id )
 );

CREATE  TABLE "public".words ( 
	topic_id             integer  NOT NULL  ,
	id                   integer  NOT NULL GENERATED  ALWAYS AS IDENTITY ,
	word                 varchar  NOT NULL  ,
	word_translation     varchar  NOT NULL  ,
	usage_example        varchar    ,
	usage_example_translation varchar    ,
	CONSTRAINT pk_words PRIMARY KEY ( id )
 );

ALTER TABLE "public".learning ADD CONSTRAINT fk_learning_users FOREIGN KEY ( user_id ) REFERENCES "public".users( id );

ALTER TABLE "public".learning ADD CONSTRAINT fk_learning_words FOREIGN KEY ( word_id ) REFERENCES "public".words( id );

ALTER TABLE "public".test ADD CONSTRAINT fk_test_users FOREIGN KEY ( user_id ) REFERENCES "public".users( id );

ALTER TABLE "public".test ADD CONSTRAINT fk_test_words FOREIGN KEY ( word_id ) REFERENCES "public".words( id );

ALTER TABLE "public".topics ADD CONSTRAINT fk_topics_users FOREIGN KEY ( user_id ) REFERENCES "public".users( id );

ALTER TABLE "public".users ADD CONSTRAINT fk_users_topics FOREIGN KEY ( topic_id ) REFERENCES "public".topics( id );

ALTER TABLE "public".words ADD CONSTRAINT fk_words_topics FOREIGN KEY ( topic_id ) REFERENCES "public".topics( id );