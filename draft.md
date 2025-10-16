включаем/не включаем в ридми

# Дорожная карта

* v1: поиск/фильтры/отзывы/пагинация/модерация/SSO.
* v1.1: экспорт/импорт данных, объединение дублей, улучшенный поиск.
* v1.2: персональные рекомендации (подсказка преподавателей по интересам), дашборды аналитики.
* v2: мобильная версия/приложение, уведомления об ответах/изменениях рейтинга.

# Модель данных (предложение для PostgreSQL/Django)

> Примечание: для простоты и скорости чтения рейтинги вынесены в поля самой таблицы `Review` (уменьшаем JOIN’ы на списках). При желании можно отделить в `Rating`.

* **Teacher**
  Поля:
  `id UUID PK`, `full_name TEXT`, `tab_number TEXT UNIQUE`, `photo_url TEXT`, `dept TEXT NULL`,
  таймстемпы: `created_at timestamptz`, `updated_at timestamptz`.
  Индексы:

  * `btree (tab_number)` (UNIQUE)
  * `GIN (full_name gin_trgm_ops)` для поиска по части ФИО (расширение `pg_trgm`).
  * (опц.) FTS: `to_tsvector('russian', full_name)` + GIN.

* **Tag**
  Поля:
  `id UUID PK`, `name_unique CITEXT UNIQUE` (нормализованное имя), `display_name TEXT`, `created_by UUID NULL -> User`, `status TEXT CHECK (status in ('active','hidden','pending')) DEFAULT 'active'`, таймстемпы.
  Индексы:

  * `btree (lower(name_unique))` (фактически обеспечивает case-insensitive уникальность через CITEXT).

* **TeacherTag** (многие-ко-многим)
  Поля:
  `teacher_id UUID FK -> Teacher`, `tag_id UUID FK -> Tag`, PK (`teacher_id`, `tag_id`).
  Индексы:

  * `btree (tag_id, teacher_id)` для фильтрации по тегам.

* **User**
  Поля:
  `id UUID PK`, `email CITEXT UNIQUE` или `sso_id TEXT UNIQUE`, `role TEXT CHECK (role in ('student','moderator','admin')) DEFAULT 'student'`, `banned_until timestamptz NULL`, таймстемпы.

* **Subject** *(опционально для поля «предмет»)*
  Поля:
  `id UUID PK`, `name TEXT UNIQUE`.

* **Review**
  Поля:
  `id UUID PK`, `teacher_id UUID FK -> Teacher`, `user_id UUID FK -> User`,
  `subject_id UUID NULL FK -> Subject`, `study_year SMALLINT CHECK (study_year BETWEEN 1 AND 10)`,
  `comment_text TEXT`, `created_at timestamptz DEFAULT now()`,
  `is_deleted BOOLEAN DEFAULT FALSE`, `visibility TEXT CHECK (visibility in ('public','hidden','reported')) DEFAULT 'public'`,
  **оценки (INT 1..5):** `rating_overall`, `rating_difficulty`, `rating_interest`, `rating_organization`, `rating_fairness` (CHECK 1..5).
  Ограничения/индексы:

  * **Partial unique**: один активный отзыв на преподавателя от пользователя

    ```sql
    CREATE UNIQUE INDEX ux_review_unique_active
      ON review (teacher_id, user_id)
      WHERE is_deleted = FALSE;
    ```
  * `btree (teacher_id, created_at DESC)` для ленты отзывов.

* **AbuseReport**
  Поля:
  `id UUID PK`, `review_id UUID FK -> Review`, `reason TEXT`, `status TEXT CHECK (status in ('new','in_review','resolved','rejected')) DEFAULT 'new'`, `created_at timestamptz`.
  Индексы:

  * `btree (status, created_at DESC)`.

* **TagSuggestion**
  Поля:
  `id UUID PK`, `name CITEXT`, `proposed_by UUID FK -> User`, `status TEXT CHECK (status in ('pending','approved','rejected')) DEFAULT 'pending'`, `created_at timestamptz`.
  Индексы:

  * `btree (lower(name))`, уникальность по нормализованному имени и статусу `approved`.

**Агрегации и производительность**

* В `Teacher` держим денормализованные поля: `avg_overall NUMERIC(3,2)`, `reviews_count INT` — обновляются фоново через Celery (или триггерами) при изменении отзывов.
* Счётчики по тегам — материализованное представление (`REFRESH CONCURRENTLY`) или кэш Redis с периодической ресинхронизацией.
* Поиск по ФИО: расширение `pg_trgm`

  ```sql
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE INDEX ix_teacher_full_name_trgm
    ON teacher USING GIN (full_name gin_trgm_ops);
  ```
* Тяжёлые списки отзывов — строгая серверная пагинация (`LIMIT/OFFSET` или keyset).

**Связки (ключевые)**

* `Teacher 1—N Review`
* `Review N—1 User`
* `Teacher N—M Tag` (через `TeacherTag`)
* `Review N—1 Subject` (опционально)

Если нужно — накину Django-модели/миграции под эту схему (с валидаторами и админкой) и пример запросов DRF + фильтров.
