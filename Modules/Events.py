class Event(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __iadd__(self, other):
        self.append(other)
        return self

    # make it use -=
    def __isub__(self, other):
        self.remove(other)
        return self


# Static class to manage events
class EventManager:
    set_dataset_event = Event()
    set_annotations_event = Event()
    set_model_event = Event()
    set_predictions_event = Event()
    enable_inspector_event = Event()
    darkmode_switch_event = Event()
    update_inspector_switch_event = Event()

    set_compare_dataset_event = Event()
    set_compare_type_event = Event()

    set_compare_predictions_event = Event()
    set_compare_types_event = Event()
    set_compare_ap_event = Event()
    set_compare_ar_event = Event()
