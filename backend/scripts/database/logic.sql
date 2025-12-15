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

-- Upsert teacher from scraper
CREATE OR REPLACE PROCEDURE upsert_teacher(
  p_isu INTEGER,
  p_name TEXT,
  p_photo_url TEXT DEFAULT NULL,
  p_phone TEXT DEFAULT NULL,
  p_url TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO teachers (isu, name, photo_url, phone, url)
  VALUES (p_isu, p_name, p_photo_url, p_phone, p_url)
  ON CONFLICT (isu) DO UPDATE
    SET name = EXCLUDED.name,
        photo_url = COALESCE(EXCLUDED.photo_url, teachers.photo_url),
        phone = COALESCE(EXCLUDED.phone, teachers.phone),
        url = COALESCE(EXCLUDED.url, teachers.url),
        updated_at = now();
END;
$$;

-- Attach contact to teacher by ISU if not exists
CREATE OR REPLACE PROCEDURE ensure_contact(
  p_teacher_isu INTEGER,
  p_contact_type TEXT,
  p_url TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_teacher_id BIGINT;
  v_exists BOOLEAN;
BEGIN
  SELECT id INTO v_teacher_id FROM teachers WHERE isu = p_teacher_isu;
  IF v_teacher_id IS NULL THEN
    RAISE EXCEPTION 'Teacher with ISU % not found', p_teacher_isu;
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM contacts
    WHERE teacher_id = v_teacher_id AND contact_type = p_contact_type AND url = p_url
  ) INTO v_exists;

  IF NOT v_exists THEN
    INSERT INTO contacts (contact_type, teacher_id, url)
    VALUES (p_contact_type, v_teacher_id, p_url);
  END IF;
END;
$$;

CREATE INDEX IF NOT EXISTS idx_reviews_teacher_subject_active ON reviews (teacher_id, subject_id) WHERE is_deleted IS NOT TRUE;
CREATE INDEX IF NOT EXISTS idx_review_tags_tag_id ON review_tags (tag_id);
CREATE INDEX IF NOT EXISTS idx_contacts_teacher_id ON contacts (teacher_id);
CREATE INDEX IF NOT EXISTS idx_moderation_actions_target_id ON moderation_actions (target_id);
CREATE INDEX IF NOT EXISTS idx_black_list_user_id ON black_list (user_id);