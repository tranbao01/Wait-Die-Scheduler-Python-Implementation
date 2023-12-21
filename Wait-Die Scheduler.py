from collections import defaultdict
class Action:
  """
  This is the Action class.
  """
  def __init__(self, object_, transaction, type_):
    self.object_ = object_
    self.transaction = transaction
    assert type_ in ("WRITE", "COMMIT", "ROLLBACK", "LOCK", "UNLOCK", "WAIT")
    self.type_ = type_
  def __str__(self):
    return f"Action('{self.object_}', '{self.transaction}', '{self.type_}')"
  __repr__ = __str__
  def __eq__(self, other):
    return ((self.object_ == other.object_) and
      (self.transaction == other.transaction) and
      (self.type_ == other.type_))



# Do not modify any code above this line


def wait_die_scheduler(actions):
    result = []
    transaction_order = {}
    object_dict = {}
    remove_dict = defaultdict(list)
    transaction_action = defaultdict(list)
    i = 0

    def process_write_action(action):
        nonlocal result
        nonlocal object_dict
        nonlocal transaction_order

        if action.object_ not in object_dict:
            object_dict[action.object_] = [True, action.transaction]
            result.append(Action(action.object_, action.transaction, 'LOCK'))
            result.append(Action(action.object_, action.transaction, 'WRITE'))
            remove_dict[action.transaction].append(action)
        else:
            if transaction_order[action.transaction] < transaction_order[object_dict[action.object_][1]]:
                result.append(Action('NA', action.transaction, 'WAIT'))
                transaction_action_list.insert(0, action)
            elif transaction_order[action.transaction] == transaction_order[object_dict[action.object_][1]]:
                result.append(Action(action.object_, action.transaction, 'WRITE'))
                remove_dict[action.transaction].append(action)
            else:
                result.append(Action('NA', action.transaction, 'ROLLBACK'))
                unlock_objects(action.transaction)
                remove_dict[action.transaction].append(action)
                transaction_action[transaction] = remove_dict[action.transaction] + transaction_action[transaction]
                remove_dict[action.transaction] = []

    def unlock_objects(transaction):
        nonlocal result
        nonlocal object_dict

        objects_unlock = [e for e in object_dict if object_dict[e][1] == transaction]
        objects_unlock.sort()
        for e in objects_unlock:
            result.append(Action(e, transaction, 'UNLOCK'))
            object_dict.pop(e)

    def process_commit_action(action):
        nonlocal result
        nonlocal object_dict
        nonlocal transaction_action
        nonlocal remove_dict

        result.append(Action('NA', action.transaction, 'COMMIT'))
        unlock_objects(action.transaction)
        transaction_action.pop(action.transaction)
        remove_dict[action.transaction] = []

    for action in actions:
        if action.transaction not in transaction_order:
            transaction_order[action.transaction] = i
            i += 1

    for action in actions:
        if action.transaction not in transaction_action:
            transaction_action[action.transaction] = []

    while len(transaction_action) > 0:
        if len(actions) > 0:
            action_pop = actions.pop(0)
            transaction_action[action_pop.transaction].append(action_pop)
        for transaction in sorted(transaction_action):
            transaction_action_list = transaction_action[transaction]
            if len(transaction_action_list) > 0:
                action = transaction_action_list.pop(0)
                if action.type_ == 'WRITE':
                    process_write_action(action)
                elif action.type_ == 'COMMIT':
                    process_commit_action(action)

    return result
