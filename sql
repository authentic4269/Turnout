              Table "public.events"
   Column    |          Type          | Modifiers 
-------------+------------------------+-----------
 title       | character varying(40)  | 
 description | character varying(800) | 
 uid         | integer                | 
 event_id    | integer                | not null
Indexes:
    "events_pkey" PRIMARY KEY, btree (event_id)
Foreign-key constraints:
    "events_uid_fkey" FOREIGN KEY (uid) REFERENCES users(fb_id)
Referenced by:
    TABLE "reminders" CONSTRAINT "reminders_event_id_fkey" FOREIGN KEY (event_id) REFERENCES events(event_id)


               Table "public.reminders"
   Column    |            Type             | Modifiers 
-------------+-----------------------------+-----------
 send_time   | timestamp without time zone | 
 reminder_id | integer                     | 
 event_id    | integer                     | 
 user_id     | integer                     | 
 type        | integer                     | 
Foreign-key constraints:
    "reminders_event_id_fkey" FOREIGN KEY (event_id) REFERENCES events(event_id)
    "reminders_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(fb_id)

                Table "public.users"
     Column      |         Type          | Modifiers 
-----------------+-----------------------+-----------
 name            | character varying(40) | 
 email           | character varying(40) | 
 auto_add        | boolean               | 
 carrier         | integer               | 
 remind_type     | integer               | 
 post_by_default | boolean               | 
 post_time       | integer               | 
 fb_id           | integer               | not null
Indexes:
    "users_pkey" PRIMARY KEY, btree (fb_id)
Referenced by:
    TABLE "events" CONSTRAINT "events_uid_fkey" FOREIGN KEY (uid) REFERENCES users(fb_id)
    TABLE "reminders" CONSTRAINT "reminders_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(fb_id)


