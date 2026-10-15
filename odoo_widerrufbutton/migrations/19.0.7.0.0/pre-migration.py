def migrate(cr, version):
    # Preserve historically unreliable flags before recomputing truthful delivery evidence.
    cr.execute("ALTER TABLE widerruf_record ADD COLUMN IF NOT EXISTS legacy_confirmation_mail_sent boolean")
    cr.execute("ALTER TABLE widerruf_record ADD COLUMN IF NOT EXISTS legacy_confirmation_mail_sent_at timestamp")
    cr.execute("UPDATE widerruf_record SET legacy_confirmation_mail_sent=confirmation_mail_sent, legacy_confirmation_mail_sent_at=confirmation_mail_sent_at WHERE legacy_confirmation_mail_sent IS NULL")
    cr.execute("ALTER TABLE widerruf_record ADD COLUMN IF NOT EXISTS legacy_delivery_evidence jsonb")
    cr.execute("""UPDATE widerruf_record SET legacy_delivery_evidence=jsonb_build_object(
        'confirmation_mail_sent',confirmation_mail_sent,'confirmation_mail_sent_at',confirmation_mail_sent_at,
        'internal_mail_sent',internal_mail_sent,'internal_mail_sent_at',internal_mail_sent_at,
        'customer_status_mail_sent_at',customer_status_mail_sent_at)
        WHERE legacy_delivery_evidence IS NULL""")
