import uuid
from django.db import models
import random

class Raffle(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.TextField()
    total_tickets = models.IntegerField()
    winners_drawn = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    available_tickets = models.IntegerField()

    # List starting from the latest(desc order)
    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return self.name

    """ returns a raffle ticket in a non-sequential order"""
    def get_ticket_number(self):
        # get all existing ticket numbers in a list
        existing_ticket_numbers = list(
            self.tickets.values_list('ticket_number', flat=True))
        # get a random ticket from 0....total_tickets excluding the ones already issues
        next_ticket = random.choice([i for i in range(1, self.total_tickets+1)
                                     if i not in existing_ticket_numbers])
        return next_ticket

    """ returns a list of winners"""
    def draw_winners(self):
        #get list of ticket_numbers
        ticket_numbers = list(self.tickets.values_list('ticket_number', flat=True))
        #draw a random winner(ticket) for each prize
        for prize in self.prizes.all():
            for i in range(0, prize.amount):
                random.shuffle(ticket_numbers)
                winning_ticket = ticket_numbers.pop()
                Ticket.objects.filter(id=winning_ticket).update(
                    has_won=True,
                    prize=prize.name
                )
        # set raffle winners_drawn     
        self.winners_drawn = True
        self.save()
        return Ticket.objects.filter(has_won=True)


class Ticket(models.Model):
    verification_code = models.UUIDField(editable=False, default=uuid.uuid4)
    raffle = models.ForeignKey(Raffle, related_name='tickets', on_delete=models.CASCADE)
    ticket_number = models.IntegerField()
    has_won = models.BooleanField(default=False)
    prize = models.CharField(default=None, max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # List starting from the first(asc order)
    class Meta:
        ordering = ('timestamp',)


class Prize(models.Model):
    name = models.TextField()
    amount = models.IntegerField()
    raffle = models.ForeignKey(Raffle, related_name='prizes', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
