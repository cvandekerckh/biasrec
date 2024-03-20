-- (A) STAR RATING TABLE
CREATE TABLE `star_rating` (
  `product_id` INTEGER  NOT NULL,
  `user_id` INTEGER  NOT NULL,
  `rating` INTEGER NOT NULL DEFAULT '1',
  PRIMARY KEY (`product_id`,`user_id`)
);

-- (B) DUMMY DATA
INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES
(1, 900, 1),
(1, 901, 2),
(1, 902, 3),
(1, 903, 4),
(1, 904, 5);