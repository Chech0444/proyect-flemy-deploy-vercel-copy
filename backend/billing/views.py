from django.utils import timezone
from datetime import timedelta
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription, UserRole, Notification, NotificationType
from billing.models import Transaction

class SimulatedPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Limpieza robusta de datos
        card_number = str(request.data.get("card_number", "")).replace(" ", "").replace("-", "")
        cvv = str(request.data.get("cvv", ""))
        expiry = str(request.data.get("expiry", "")).replace("/", "")
        plan = request.data.get("plan", "PREMIUM")

        print(f"DEBUG: Intento de pago - Tarjeta: {card_number[-4:]} CVV: {cvv} Plan: {plan}")

        # Simulación de Pasarela
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

        # Si el pago es "exitoso"
        try:
            user = request.user
            user.role = UserRole.PREMIUM
            user.save(update_fields=["role"])

            # Crear o actualizar suscripción
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

            # Notificación de bienvenida
            Notification.objects.create(
                user=user,
                type=NotificationType.SYSTEM,
                title="¡Bienvenido a Flemy Premium!",
                message=f"Tu plan {plan} ha sido activado. Ahora tienes acceso a todos los cursos y herramientas de IA.",
                action_url="/dashboard"
            )

            # --- NUEVO: Registrar Transacción Real en DB ---
            Transaction.objects.create(
                user=user,
                amount=29.99 if plan == "MONTHLY" else 299.99, # Precios fijos simulados
                card_last4=card_number[-4:],
                status="completed"
            )
            # ---------------------------------------------

            return Response({
                "message": "Pago procesado exitosamente. ¡Ya eres un usuario Premium!",
                "role": user.role,
                "expiry": end_date.strftime("%Y-%m-%d")
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"ERROR CRÍTICO EN PAGO: {str(e)}")
            return Response(
                {"detail": f"Error interno al procesar la suscripción: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ===================================================
# REAL WOMPI INTEGRATION VIEWS (PSE / Nequi / Card)
# ===================================================
import requests
from django.conf import settings

class WompiConfigView(APIView):
    """
    Exposes Wompi Public configuration so the frontend 
    can dynamic load public keys and API URLs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "public_key": settings.WOMPI_PUBLIC_KEY,
            "api_url": settings.WOMPI_API_URL,
        }, status=status.HTTP_200_OK)


class WompiVerifyView(APIView):
    """
    Verifies Wompi Transaction status by contacting Wompi API directly.
    Saves subscription status upon approval.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        plan = request.data.get("plan", "MONTHLY")

        if not transaction_id:
            return Response({"detail": "Falta el ID de transacción de Wompi."}, status=status.HTTP_400_BAD_REQUEST)

        # Call Wompi API
        url = f"{settings.WOMPI_API_URL}/transactions/{transaction_id}"
        print(f"DEBUG: Consultando Wompi para verificación. URL: {url}")
        
        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                return Response(
                    {"detail": f"No se pudo consultar la transacción en Wompi (Código {res.status_code})."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data = res.json().get("data", {})
            status_wompi = data.get("status")
            amount_in_cents = data.get("amount_in_cents", 0)
            amount = amount_in_cents / 100
            payment_method_type = data.get("payment_method_type", "PSE")

            print(f"DEBUG: Wompi Response Status: {status_wompi} for ID: {transaction_id}")

            if status_wompi == "APPROVED":
                user = request.user
                user.role = UserRole.PREMIUM
                user.save(update_fields=["role"])

                # Create subscription
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

                # Send premium welcome notification
                Notification.objects.create(
                    user=user,
                    type=NotificationType.SYSTEM,
                    title="¡Pago Confirmado! Bienvenido a Premium",
                    message=f"Tu transacción con Wompi fue aprobada. Ya tienes acceso Premium activo hasta {end_date.strftime('%Y-%m-%d')}.",
                    action_url="/dashboard"
                )

                # Log Transaction
                Transaction.objects.update_or_create(
                    user=user,
                    card_last4=transaction_id[-4:], # Store last 4 of Wompi ID for trace
                    defaults={
                        "amount": amount,
                        "status": "completed"
                    }
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
                    "detail": f"El pago no fue aprobado. Estado de Wompi: {status_wompi}"
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"ERROR CRÍTICO VERIFICACIÓN WOMPI: {str(e)}")
            return Response(
                {"detail": f"Error interno en verificación de pago: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

