/* Create vote2kick table */
CREATE TABLE `vote2kick` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `author_user_id` int(11) NOT NULL,
    `member_user_id` int(11) NOT NULL,
    `message_id` int(11) NULL,
    `guild_id` int(11) NOT NULL,
    `reason` varchar(255) NULL,
    `created_at` datetime NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `id` (`id`) USING BTREE
);

CREATE TABLE `queue` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `user_id` int(11) NOT NULL,

)