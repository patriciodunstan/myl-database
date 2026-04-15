import { useState } from 'react';
import { submitContact } from '../api/contact';
import type { ContactForm } from '../types';

export function Contact() {
  const [formData, setFormData] = useState<ContactForm>({
    nombre: '',
    email: '',
    tipo: 'Sugerencia',
    mensaje: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{
    show: boolean;
    message: string;
    isError: boolean;
  }>({ show: false, message: '', isError: false });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFeedback({ show: false, message: '', isError: false });

    try {
      await submitContact(formData);
      setFeedback({
        show: true,
        message: '¡Mensaje enviado! Gracias por tu feedback.',
        isError: false,
      });
      setFormData({ nombre: '', email: '', tipo: 'Sugerencia', mensaje: '' });
    } catch (error: any) {
      setFeedback({
        show: true,
        message: `Error: ${error.message || 'Error al enviar'}`,
        isError: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  return (
    <div className="banlist-container">
      <div className="banlist-header">
        <h2 className="banlist-title">Contacto & Sugerencias</h2>
      </div>
      <p style={{
        color: 'var(--color-text-secondary)',
        marginBottom: 'var(--spacing-6)',
      }}>
        ¿Encontraste un error, tenés una sugerencia o querés ponerte en contacto? Completá el formulario y lo revisamos.
      </p>
      <form onSubmit={handleSubmit} style={{
        maxWidth: '560px',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-4)',
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
          <label style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-small)',
            fontWeight: 'var(--font-weight-medium)',
          }}>
            Nombre *
          </label>
          <input
            id="contacto-nombre"
            type="text"
            placeholder="Tu nombre"
            required
            name="nombre"
            value={formData.nombre}
            onChange={handleInputChange}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-3) var(--spacing-4)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-body)',
              outline: 'none',
            }}
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
          <label style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-small)',
            fontWeight: 'var(--font-weight-medium)',
          }}>
            Email (opcional)
          </label>
          <input
            id="contacto-email"
            type="email"
            placeholder="tucorreo@ejemplo.com"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-3) var(--spacing-4)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-body)',
              outline: 'none',
            }}
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
          <label style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-small)',
            fontWeight: 'var(--font-weight-medium)',
          }}>
            Tipo
          </label>
          <select
            id="contacto-tipo"
            name="tipo"
            value={formData.tipo}
            onChange={handleInputChange}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-3) var(--spacing-4)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-body)',
              outline: 'none',
            }}
          >
            <option value="Sugerencia">Sugerencia</option>
            <option value="Consulta">Consulta</option>
            <option value="Reporte de error">Reporte de error</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-2)' }}>
          <label style={{
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-small)',
            fontWeight: 'var(--font-weight-medium)',
          }}>
            Mensaje *
          </label>
          <textarea
            id="contacto-mensaje"
            rows={5}
            placeholder="Escribí tu mensaje acá..."
            required
            name="mensaje"
            value={formData.mensaje}
            onChange={handleInputChange}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-3) var(--spacing-4)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-body)',
              outline: 'none',
              resize: 'vertical',
              fontFamily: 'inherit',
            }}
          />
        </div>
        <div>
          <button
            id="contacto-submit"
            type="submit"
            disabled={isSubmitting}
            style={{
              background: 'var(--color-accent)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--spacing-3) var(--spacing-8)',
              fontSize: 'var(--font-size-body)',
              fontWeight: 'var(--font-weight-semibold)',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'background var(--transition-fast)',
            }}
          >
            {isSubmitting ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
        {feedback.show && (
          <div
            id="contacto-feedback"
            style={{
              display: 'block',
              padding: 'var(--spacing-3) var(--spacing-4)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-small)',
              background: feedback.isError
                ? 'rgba(239,68,68,0.1)'
                : 'rgba(74,222,128,0.1)',
              color: feedback.isError
                ? 'var(--color-error)'
                : 'var(--color-success)',
              border: '1px solid',
              borderColor: feedback.isError
                ? 'var(--color-error)'
                : 'var(--color-success)',
            }}
          >
            {feedback.message}
          </div>
        )}
      </form>
    </div>
  );
}
