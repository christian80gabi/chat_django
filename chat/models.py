from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# ---------------------------------------------------------------------------- #
#                                  User Model                                  #
# ---------------------------------------------------------------------------- #

class UserProfile(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'chat_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# ---------------------------------------------------------------------------- #
#                                 Message Model                                #
# ---------------------------------------------------------------------------- #
class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipient')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ('-date',)

    # function gets all messages between 'the' two users (requires your pk and the other user pk)
    def get_all_messages(self, id_2):
        # get messages between the two users, sort them by date(reverse) and add them to the list
        message1 = Message.objects.filter(
            sender_id=self, recipient_id=id_2
        ).order_by('-date')
        messages = [message1[x] for x in range(len(message1))]
        message2 = Message.objects.filter(
            sender_id=id_2, recipient_id=self
        ).order_by('-date')
        messages.extend(message2[x] for x in range(len(message2)))
        # because the function is called when viewing the chat, we'll return all messages as read
        for message in messages:
            message.is_read = True
        # sort the messages by date
        messages.sort(key=lambda x: x.date, reverse=False)
        return messages

    # function gets all messages between 'any' two users (requires your pk)
    def get_message_list(self):
        # get all the messages
        m = []  # stores all messages sorted by latest first
        j = []  # stores all usernames from the messages above after removing duplicates
        k = []  # stores the latest message from the sorted usernames above
        for message in Message.objects.all():
            for_you = message.recipient == self
            from_you = message.sender == self
            if for_you or from_you:
                m.append(message)
                m.sort(key=lambda x: x.sender.username)  # sort the messages by senders
                m.sort(key=lambda x: x.date, reverse=True)  # sort the messages by date

        # remove duplicates usernames and get single message(latest message) per username(other user) (between you and other user)
        for i in m:
            if i.sender.username not in j or i.recipient.username not in j:
                j.extend((i.sender.username, i.recipient.username))
                k.append(i)

        return k
