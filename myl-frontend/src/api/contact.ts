import { fetchAPI } from './client';
import type { ContactForm, ContactResponse } from '../types';

export async function submitContact(form: ContactForm): Promise<ContactResponse> {
  return fetchAPI<ContactResponse>('/contacto', {
    method: 'POST',
    body: JSON.stringify(form),
  });
}
