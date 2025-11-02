CREATE TABLE `member` (
	`id`	INT	NOT NULL,
	`email`	VARCHAR(255)	NOT NULL,
	`password`	VARCHAR(255)	NOT NULL,
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `course` (
	`id`	INT	NOT NULL,
	`owner_id`	INT	NOT NULL,
	`title`	VARCHAR(255)	NOT NULL,
	`description`	TEXT	NULL,
	`difficulty`	ENUM('easy','medium','hard')	NULL	DEFAULT 'medium',
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `chapter` (
	`id`	INT	NOT NULL,
	`course_id`	INT	NOT NULL,
	`owner_id`	INT	NOT NULL,
	`title`	VARCHAR(255)	NOT NULL,
	`description`	TEXT	NULL,
	`order_index`	INT	NULL,
	`is_active`	BOOLEAN	NULL,
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `concept` (
	`id`	INT	NOT NULL,
	`chapter_id`	INT	NOT NULL,
	`owner_id`	INT	NOT NULL,
	`title`	VARCHAR(255)	NOT NULL,
	`content`	TEXT	NOT NULL,
	`example`	TEXT	NULL,
	`is_complete`	BOOLEAN	NULL,
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `exercise` (
	`id`	INT	NOT NULL,
	`chapter_id`	INT	NOT NULL,
	`owner_id`	INT	NOT NULL,
	`question`	TEXT	NOT NULL,
	`answer`	TEXT	NOT NULL,
	`explanation`	TEXT	NULL,
	`difficulty`	ENUM('easy','medium','hard')	NULL	DEFAULT 'medium',
	`is_complete`	BOOLEAN	NULL,
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `quiz` (
	`id`	INT	NOT NULL,
	`chapter_id`	INT	NOT NULL,
	`owner_id`	INT	NOT NULL,
	`question`	TEXT	NOT NULL,
	`options`	JSON	NULL,
	`correct_answer`	VARCHAR(255)	NOT NULL,
	`explanation`	TEXT	NULL,
	`type`	ENUM('multiple','short','boolean')	NULL	DEFAULT 'multiple',
	`created_at`	DATETIME	NULL,
	`updated_at`	DATETIME	NULL	DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE `member` ADD CONSTRAINT `PK_MEMBER` PRIMARY KEY (
	`id`
);

ALTER TABLE `course` ADD CONSTRAINT `PK_COURSE` PRIMARY KEY (
	`id`,
	`owner_id`
);

ALTER TABLE `chapter` ADD CONSTRAINT `PK_CHAPTER` PRIMARY KEY (
	`id`,
	`course_id`,
	`owner_id`
);

ALTER TABLE `concept` ADD CONSTRAINT `PK_CONCEPT` PRIMARY KEY (
	`id`,
	`chapter_id`,
	`owner_id`
);

ALTER TABLE `exercise` ADD CONSTRAINT `PK_EXERCISE` PRIMARY KEY (
	`id`,
	`chapter_id`,
	`owner_id`
);

ALTER TABLE `quiz` ADD CONSTRAINT `PK_QUIZ` PRIMARY KEY (
	`id`,
	`chapter_id`,
	`owner_id`
);

ALTER TABLE `course` ADD CONSTRAINT `FK_member_TO_course_1` FOREIGN KEY (
	`owner_id`
)
REFERENCES `member` (
	`id`
);

ALTER TABLE `chapter` ADD CONSTRAINT `FK_course_TO_chapter_1` FOREIGN KEY (
	`course_id`
)
REFERENCES `course` (
	`id`
);

ALTER TABLE `chapter` ADD CONSTRAINT `FK_member_TO_chapter_1` FOREIGN KEY (
	`owner_id`
)
REFERENCES `member` (
	`id`
);

ALTER TABLE `concept` ADD CONSTRAINT `FK_chapter_TO_concept_1` FOREIGN KEY (
	`chapter_id`
)
REFERENCES `chapter` (
	`course_id`
);

ALTER TABLE `concept` ADD CONSTRAINT `FK_chapter_TO_concept_2` FOREIGN KEY (
	`owner_id`
)
REFERENCES `chapter` (
	`owner_id`
);

ALTER TABLE `exercise` ADD CONSTRAINT `FK_chapter_TO_exercise_1` FOREIGN KEY (
	`chapter_id`
)
REFERENCES `chapter` (
	`course_id`
);

ALTER TABLE `exercise` ADD CONSTRAINT `FK_chapter_TO_exercise_2` FOREIGN KEY (
	`owner_id`
)
REFERENCES `chapter` (
	`owner_id`
);

ALTER TABLE `quiz` ADD CONSTRAINT `FK_chapter_TO_quiz_1` FOREIGN KEY (
	`chapter_id`
)
REFERENCES `chapter` (
	`course_id`
);

ALTER TABLE `quiz` ADD CONSTRAINT `FK_chapter_TO_quiz_2` FOREIGN KEY (
	`owner_id`
)
REFERENCES `chapter` (
	`owner_id`
);

