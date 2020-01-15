class EventSerialization:

  @staticmethod
  def standard(event):
    return dict(
      name=event.name,
      ns=event.namespace,
      reason=event.reason,
      message=event.message,
      type=event.severity,
      meaning=event.meaning(),
      occurred_at=str(event.occurred_at)
    )