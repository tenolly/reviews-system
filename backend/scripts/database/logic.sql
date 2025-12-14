-- optional!
CREATE FUNCTION check_tag_count() RETURNS trigger AS $$
DECLARE n INT;
BEGIN
  SELECT COUNT(*) INTO n FROM review_tags WHERE review_id = NEW.review_id;
  IF n >= 10 THEN
    RAISE EXCEPTION 'Too many tags';
  END IF;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER check_tag_count_trigger
  BEFORE UPDATE OR INSERT ON review_tags
  FOR EACH ROW
  EXECUTE FUNCTION check_tag_count();

CREATE OR REPLACE PROCEDURE add_user(
  p_username TEXT,
  p_password_hash TEXT,
  p_email TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, password_hash, email)
    VALUES (p_username, p_password_hash, p_email);

    -- Автоматический COMMIT происходит после завершения процедуры,
    -- если не был вызван явный COMMIT или ROLLBACK внутри.
END;
$$;

CREATE INDEX IF NOT EXISTS idx_reviews_teacher_subject_active ON reviews (teacher_id, subject_id) WHERE is_deleted IS NOT TRUE;
CREATE INDEX IF NOT EXISTS idx_review_tags_tag_id ON review_tags (tag_id);
CREATE INDEX IF NOT EXISTS idx_contacts_teacher_id ON contacts (teacher_id);
CREATE INDEX IF NOT EXISTS idx_moderation_actions_target_id ON moderation_actions (target_id);
CREATE INDEX IF NOT EXISTS idx_black_list_user_id ON black_list (user_id);