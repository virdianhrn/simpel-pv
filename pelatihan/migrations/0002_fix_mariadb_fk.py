from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("pelatihan", "0001_initial"),  # <- adjust
    ]

    operations = [
        # 1) make sure the parent table is InnoDB + utf8mb4
        migrations.RunSQL(
            sql="""
            ALTER TABLE pelatihan_pelatihan
              ENGINE=InnoDB,
              CONVERT TO CHARACTER SET utf8mb4
              COLLATE utf8mb4_unicode_ci;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 2) same for the child, so its indexes are BTREE
        migrations.RunSQL(
            sql="""
            ALTER TABLE pelatihan_pelatihaninstruktur
              ENGINE=InnoDB,
              CONVERT TO CHARACTER SET utf8mb4
              COLLATE utf8mb4_unicode_ci;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 3) recreate the unique index in a way MariaDB likes
        # if Django already made it, this will be a no-op on second run
        migrations.RunSQL(
            sql="""
            ALTER TABLE pelatihan_pelatihaninstruktur
            DROP INDEX IF EXISTS pelatihan_pelatihaninstr_pelatihan_id_instruktur__66466c58_uniq;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
            ALTER TABLE pelatihan_pelatihaninstruktur
            ADD UNIQUE idx_peltrainst_uniq (pelatihan_id, instruktur_id, materi);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 4) finally, add the FK explicitly
        migrations.RunSQL(
            sql="""
            ALTER TABLE pelatihan_pelatihaninstruktur
            ADD CONSTRAINT fk_peltrainst_pelatihan
              FOREIGN KEY (pelatihan_id)
              REFERENCES pelatihan_pelatihan (id)
              ON DELETE CASCADE
              ON UPDATE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE pelatihan_pelatihaninstruktur
            DROP FOREIGN KEY fk_peltrainst_pelatihan;
            """,
        ),
    ]
