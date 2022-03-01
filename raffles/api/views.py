
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from raffles.models import Raffle, Ticket
from .serializers import RaffleSerializer, TicketSerializer, RaffleWinnerSerializer, TicketVerificationSerializer
from .permissions import WhitelistPermission


class RaffleView(APIView):
    permission_classes = [WhitelistPermission]

    def get(self, request, id=None):
        if id:
            """ get raffle details """
            try:
                query_set = Raffle.objects.get(id=id)
                serializer = RaffleSerializer(query_set)
            except Raffle.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            """ List raffles starting from latest """
            query_set = Raffle.objects.all()
            serializer = RaffleSerializer(query_set, many=True)

        return Response(serializer.data)

    def post(self, request):
        """ Create a new raffle  """
        serializer = RaffleSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RaffleParticipateView(APIView):

    def post(self, request, id=None):
        """ Get a raffle ticket   """
        try:
            raffle = Raffle.objects.get(id=id)
            # Check if tickets to this raffle are no longer available
            if raffle.available_tickets == 0:
                return Response({"Tickets to this raffle are no longer available"}, status=status.HTTP_410_GONE)

            request.data['raffle_id'] = id  # fetch raffle id from get
            request.data['ip_address'] = request.META.get(
                "REMOTE_ADDR")  # fetch current request ip_address
            existing_ip_address = list(
                raffle.tickets.values_list('ip_address', flat=True))
            current_ip_request = request.META.get("REMOTE_ADDR")

            # Check if ip address has already participated in this raffle
            if current_ip_request in existing_ip_address:
                return Response({"Your ip address has already participated in this raffle"}, status=status.HTTP_403_FORBIDDEN)

            serializer = TicketSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Raffle.DoesNotExist:
            # EXCEPTION: Raffle does not exist"
            return Response({"Invalid Raffle id"}, status=status.HTTP_400_BAD_REQUEST)


class RaffleWinnersView(APIView):

    permission_classes = [WhitelistPermission]

    def get(self, request, id=None):
        """ List winners of a raffle  """
        try:
            raffle = Raffle.objects.get(id=id)
            query_set = raffle.tickets.filter(has_won=True)
            serializer = RaffleWinnerSerializer(query_set, many=True)
            return Response(serializer.data)
        except Raffle.DoesNotExist:
            # EXCEPTION: Raffle does not exist
            return Response({"Invalid raffle id"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id=None):
        """ draw winnner  """
        try:
            raffle = Raffle.objects.get(id=id)

            # EXCEPTION: Winners can't be drawn when tickets are still available
            if raffle.available_tickets != 0:
                return Response({"Winners can't be drawn when tickets are still available"}, status=status.HTTP_403_FORBIDDEN)

            # EXCEPTION: Winners for the raffle have already been drawn"
            if raffle.winners_drawn == True:
                return Response({"Winners for the raffle have already been drawn"}, status=status.HTTP_403_FORBIDDEN)

            if raffle.winners_drawn == False and raffle.available_tickets == 0:
                query_set = raffle.draw_winners()
                serializer = RaffleWinnerSerializer(query_set, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # EXCEPTION: Winners for the raffle have not been drawn yet"
                return Response({"Winners for the raffle have not been drawn yet"}, status=status.HTTP_400_BAD_REQUEST)
        except Raffle.DoesNotExist:
            # EXCEPTION: Raffle does not exist"
            return Response({"Invalid Raffle id"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyRaffleTicketView(APIView):

    def post(self, request, id=None):
        """ verify ticket  """
        try:
            raffle = Raffle.objects.get(id=id)

            # EXCEPTION: Winners for the raffle have not been drawn yet"
            if raffle.winners_drawn == False:
                return Response({"Winners for the raffle have not been drawn yet"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                query_set = Ticket.objects.get(
                    verification_code=request.data['verification_code'],
                    ticket_number=request.data['ticket_number'])

                serializer = TicketVerificationSerializer(query_set)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Ticket.DoesNotExist:
                # EXCEPTION: Ticket does not exist"
                return Response({"Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

        except Raffle.DoesNotExist:
            # EXCEPTION: Ticket does not exist"
            return Response({"Invalid raffle id"}, status=status.HTTP_400_BAD_REQUEST)
