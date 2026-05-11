
import os
import django
from dotenv import load_dotenv

# Configurar entorno de Django
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.courses.services.ai_services import ai_service

def test_ai_integration():
    print("🚀 Probando integración con Google Gemini...")
    
    sample_text = """
    Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. 
    Fue creado por Guido van Rossum y lanzado por primera vez en 1991. 
    Su filosofía de diseño enfatiza la legibilidad del código, con su notable uso de sangría significativa. 
    Python es recolectado por basura y de tipado dinámico. Admite múltiples paradigmas de programación, 
    incluida la programación estructurada (especialmente procedural), orientada a objetos y funcional.
    Python se utiliza a menudo como un 'lenguaje de script' para aplicaciones web, lo que permite 
    a los desarrolladores crear contenido dinámico y aplicaciones potentes.
    """
    
    print("\n📝 Generando resumen...")
    summary = ai_service.generate_summary(sample_text)
    
    print("\n--- RESUMEN GENERADO ---")
    print(summary.get('content', 'No se pudo generar el resumen.'))
    print("\n--- PUNTOS CLAVE ---")
    for point in summary.get('key_points', []):
        print(f"• {point}")
        
    print("\n❓ Generando quiz (5 preguntas)...")
    quiz = ai_service.generate_quiz(sample_text, num_questions=5)
    
    print("\n--- QUIZ GENERADO ---")
    for i, q in enumerate(quiz):
        print(f"\n{i+1}. {q['question']}")
        for j, opt in enumerate(q['options']):
            letter = chr(65 + j)
            print(f"   {letter}) {opt}")
        print(f"   ✓ Correcta: {chr(65 + q['correct_option'])}")
        print(f"   💡 Explicación: {q.get('explanation', 'N/A')}")

if __name__ == "__main__":
    try:
        test_ai_integration()
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
