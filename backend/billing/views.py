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
