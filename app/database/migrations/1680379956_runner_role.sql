-- Moderator 1 -> 2
-- Admin 2 -> 3
UPDATE users SET role = role + 1 WHERE role > 1;
