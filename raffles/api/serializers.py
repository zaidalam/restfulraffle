
from rest_framework import serializers
from raffles.models import Raffle, Prize, Ticket
# for more  robustness, avoiding a race condition we can use
from django.db.models import F


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = ['name', 'amount']


class RaffleWinnerSerializer(serializers.ModelSerializer):
    raffle_id = serializers.UUIDField()
    ticket_number = serializers.IntegerField(required=False)
    prize = serializers.CharField(required=False)

    class Meta:
        model = Ticket
        fields = ['raffle_id', 'ticket_number', 'prize', 'verification_code']


class TicketVerificationSerializer(serializers.ModelSerializer):
    has_won = serializers.BooleanField(required=False, default=False)
    prize = serializers.CharField(required=False, default=None)
    ticket_number = serializers.IntegerField()
    verification_code = serializers.UUIDField()

    class Meta:
        model = Ticket
        fields = ['has_won', 'prize', 'ticket_number', 'verification_code']


class RaffleSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    available_tickets = serializers.IntegerField(required=False)
    prizes = PrizeSerializer(many=True, required=True)

    class Meta:
        model = Raffle
        fields = [
            'id',
            'name',
            'total_tickets',
            'winners_drawn',
            'prizes',
            'tickets',
            'available_tickets'
        ]

    def validate(self, value):
        # check if prizes are empty
        if not value['prizes']:
            raise serializers.ValidationError("No prizes")
        # check if total prizes is greater then total tickets
        if sum([prize['amount'] for prize in value['prizes']]) > value['total_tickets']:
            raise serializers.ValidationError("Too many prizes")

        return value

    def create(self, validated_data):
        # save raffle in database
        prizes_data = validated_data.pop("prizes")
        validated_data['available_tickets'] = validated_data['total_tickets']
        raffle = Raffle.objects.create(**validated_data)
        # create prizes
        for prize_data in prizes_data:
            Prize.objects.create(raffle=raffle, **prize_data)
        return raffle


class TicketSerializer(serializers.ModelSerializer):
    raffle_id = serializers.UUIDField()
    ticket_number = serializers.IntegerField(required=False)
    verification_code = serializers.UUIDField(required=False)

    class Meta:
        model = Ticket
        fields = [
            'raffle_id',
            'ticket_number',
            'verification_code',
            'ip_address'
        ]

    def create(self, validated_data):
        # save ticket in database
        raffle = Raffle.objects.get(id=validated_data['raffle_id'])
        validated_data['ticket_number'] = raffle.get_ticket_number()
        ticket = Ticket.objects.create(**validated_data)
        # available_tickets value can be effected by race conditions
        raffle.available_tickets = F('available_tickets') - 1
        raffle.save()
        return ticket
