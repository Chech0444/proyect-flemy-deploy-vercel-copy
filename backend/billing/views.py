from django.utils import timezone
from datetime import timedelta
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription, UserRole, Notification, NotificationType
from billing.models import Transaction, Product, ProductPurchase
from billing.serializers import ProductSerializer

import requests
import hashlib
from django.conf import settings
import re


TRANSACTION_ID_RE = re.compile(r'^[a-zA-Z0-9\-_]+$')


class ProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulatedPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        card_number = str(request.data.get("card_number", "")).replace(" ", "").replace("-", "")
        cvv = str(request.data.get("cvv", ""))
        expiry = str(request.data.get("expiry", "")).replace("/", "")
        plan = request.data.get("plan", "PREMIUM")

        if not card_number.endswith("4242") or len(card_number) < 16:
            return Response(
                {"detail": "La tarjeta es inválida o rechazada. Usa una que termine en 4242 (16 dígitos)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cvv != "123":
            return Response(
                {"detail": "El código CVV es incorrecto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = request.user
            user.role = UserRole.PREMIUM
            user.save(update_fields=["role"])

            duration_days = 30 if plan == "MONTHLY" else 365
            end_date = timezone.now() + timedelta(days=duration_days)

            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "end_date": end_date,
                    "is_active": True,
                    "plan_type": plan
                }
            )

            Notification.objects.create(
                user=user,
                type=NotificationType.SYSTEM,
                title="¡Bienvenido a Flemy Premium!",
                message=f"Tu plan {plan} ha sido activado. Ahora tienes acceso a todos los cursos y herramientas de IA.",
                action_url="/dashboard"
            )

            Transaction.objects.create(
                user=user,
                amount=29.99 if plan == "MONTHLY" else 299.99,
                currency="USD",
                card_last4=card_number[-4:],
                status="completed"
            )

            return Response({
                "message": "Pago procesado exitosamente. ¡Ya eres un usuario Premium!",
                "role": user.role,
                "expiry": end_date.strftime("%Y-%m-%d")
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Error interno al procesar la suscripción. Intenta de nuevo."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimulatedPurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        card_number = str(request.data.get("card_number", "")).replace(" ", "").replace("-", "")
        cvv = str(request.data.get("cvv", ""))
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"detail": "Falta el ID del producto."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not card_number.endswith("4242") or len(card_number) < 16:
            return Response(
                {"detail": "La tarjeta es inválida o rechazada. Usa una que termine en 4242 (16 dígitos)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if cvv != "123":
            return Response(
                {"detail": "El código CVV es incorrecto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = request.user
            transaction = Transaction.objects.create(
                user=user,
                amount=product.price_cop,
                currency="COP",
                card_last4=card_number[-4:],
                status="completed"
            )
            ProductPurchase.objects.create(
                user=user,
                product=product,
                transaction=transaction
            )
            Notification.objects.create(
                user=user,
                type=NotificationType.SYSTEM,
                title="¡Compra Exitosa!",
                message=f"Has adquirido '{product.name}' por ${product.price_cop} COP.",
                action_url="/dashboard"
            )
            return Response({
                "message": f"¡'{product.name}' adquirido exitosamente!",
                "product": product.name,
                "amount": product.price_cop
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Error interno al procesar la compra. Intenta de nuevo."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WompiConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "public_key": settings.WOMPI_PUBLIC_KEY,
            "api_url": settings.WOMPI_API_URL,
        }, status=status.HTTP_200_OK)


class WompiSignatureView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        reference = request.data.get("reference")
        amount_in_cents = request.data.get("amount_in_cents")
        currency = request.data.get("currency", "COP")

        if not reference or not amount_in_cents:
            return Response({"detail": "Faltan referencia o monto."}, status=status.HTTP_400_BAD_REQUEST)

        integrity_key = settings.WOMPI_INTEGRITY_KEY
        if not integrity_key:
            return Response(
                {"detail": "WOMPI_INTEGRITY_KEY no está configurada en el servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        raw = f"{reference}{amount_in_cents}{currency}{integrity_key}"
        signature = hashlib.sha256(raw.encode()).hexdigest()

        return Response({"signature": signature}, status=status.HTTP_200_OK)


class WompiVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        plan = request.data.get("plan", "MONTHLY")

        if not transaction_id:
            return Response({"detail": "Falta el ID de transacción de Wompi."}, status=status.HTTP_400_BAD_REQUEST)

        if not TRANSACTION_ID_RE.match(str(transaction_id)):
            return Response({"detail": "El ID de transacción tiene un formato inválido."}, status=status.HTTP_400_BAD_REQUEST)

        url = f"{settings.WOMPI_API_URL}/transactions/{transaction_id}"

        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                return Response(
                    {"detail": "No se pudo consultar la transacción en Wompi."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = res.json().get("data", {})
            status_wompi = data.get("status")
            amount_in_cents = data.get("amount_in_cents", 0)
            amount = amount_in_cents / 100

            if status_wompi == "APPROVED":
                user = request.user
                user.role = UserRole.PREMIUM
                user.save(update_fields=["role"])

                duration_days = 30 if plan == "MONTHLY" else 365
                end_date = timezone.now() + timedelta(days=duration_days)

                Subscription.objects.update_or_create(
                    user=user,
                    defaults={
                        "end_date": end_date,
                        "is_active": True,
                        "plan_type": plan
                    }
                )

                Notification.objects.create(
                    user=user,
                    type=NotificationType.SYSTEM,
                    title="¡Pago Confirmado! Bienvenido a Premium",
                    message=f"Tu transacción con Wompi fue aprobada. Ya tienes acceso Premium activo hasta {end_date.strftime('%Y-%m-%d')}.",
                    action_url="/dashboard"
                )

                Transaction.objects.create(
                    user=user,
                    amount=amount,
                    currency="COP",
                    card_last4="",
                    wompi_transaction_id=transaction_id,
                    status="completed"
                )

                return Response({
                    "status": "APPROVED",
                    "message": "¡Suscripción Premium activada con éxito!",
                    "role": user.role,
                    "expiry": end_date.strftime("%Y-%m-%d")
                }, status=status.HTTP_200_OK)

            elif status_wompi == "PENDING":
                return Response({
                    "status": "PENDING",
                    "message": "Tu pago con PSE está pendiente de confirmación bancaria."
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": status_wompi,
                    "detail": "El pago no fue aprobado."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": "Error interno en verificación de pago."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WompiPurchaseVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        product_id = request.data.get("product_id")

        if not transaction_id:
            return Response({"detail": "Falta el ID de transacción de Wompi."}, status=status.HTTP_400_BAD_REQUEST)
        if not TRANSACTION_ID_RE.match(str(transaction_id)):
            return Response({"detail": "El ID de transacción tiene un formato inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if not product_id:
            return Response({"detail": "Falta el ID del producto."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        url = f"{settings.WOMPI_API_URL}/transactions/{transaction_id}"

        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                return Response(
                    {"detail": "No se pudo consultar la transacción en Wompi."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = res.json().get("data", {})
            status_wompi = data.get("status")

            if status_wompi == "APPROVED":
                user = request.user
                transaction = Transaction.objects.create(
                    user=user,
                    amount=product.price_cop,
                    currency="COP",
                    card_last4="",
                    wompi_transaction_id=transaction_id,
                    status="completed"
                )
                ProductPurchase.objects.create(
                    user=user,
                    product=product,
                    transaction=transaction
                )
                Notification.objects.create(
                    user=user,
                    type=NotificationType.SYSTEM,
                    title="¡Compra Confirmada!",
                    message=f"Has adquirido '{product.name}' por ${product.price_cop} COP.",
                    action_url="/dashboard"
                )
                return Response({
                    "status": "APPROVED",
                    "message": f"¡'{product.name}' adquirido exitosamente!",
                    "product": product.name,
                    "amount": product.price_cop
                }, status=status.HTTP_200_OK)

            elif status_wompi == "PENDING":
                return Response({
                    "status": "PENDING",
                    "message": "Tu pago está pendiente de confirmación bancaria."
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": status_wompi,
                    "detail": "El pago no fue aprobado."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": "Error interno en verificación de pago."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
