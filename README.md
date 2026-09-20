# Radiografía de Sueldos — acceso interno

Dashboard de remuneraciones del sector público chileno, protegido por login
con Google institucional y restringido por dominio de correo.
Next.js + NextAuth, sin base de datos (sesión en JWT).

- `public/dashboard.html` — el dashboard en sí (HTML/CSS/JS autocontenido).
- `app/page.tsx` — ruta raíz protegida, redirige a `/dashboard.html`.
- `app/login/page.tsx` — pantalla de login.
- `lib/auth.ts` — configuración de NextAuth (proveedores + regla de quién entra).
- `proxy.ts` — protege todas las rutas salvo `/login` y `/api/auth/*`.

## 1. Instalar y probar en local

```bash
npm install
cp .env.example .env.local
```

Para probar sin configurar OAuth todavía, deja `ALLOW_ALL=true` en `.env.local`
(deja pasar a cualquiera — **solo para desarrollo**, nunca en producción) y
genera un secreto:

```bash
# En NEXTAUTH_SECRET, dentro de .env.local
openssl rand -base64 32
```

```bash
npm run dev
```

Abre http://localhost:3000 — sin sesión te manda a `/login`.

## 2. Crear credenciales de Google OAuth

1. Ve a [Google Cloud Console](https://console.cloud.google.com/) con una
   cuenta con permisos en el Workspace de la fundación (o crea un proyecto
   nuevo, es gratis).
2. **APIs & Services → OAuth consent screen**: tipo "Interno" si el proyecto
   vive dentro del Workspace de la organización (así solo cuentas del dominio
   pueden autorizar la app), o "Externo" si no.
3. **APIs & Services → Credentials → Create Credentials → OAuth client ID**,
   tipo **Web application**.
4. En "Authorized redirect URIs" agrega:
   - `http://localhost:3000/api/auth/callback/google` (para probar en local)
   - `https://<tu-dominio-de-producción>/api/auth/callback/google`
5. Copia el **Client ID** y **Client Secret** a `GOOGLE_CLIENT_ID` /
   `GOOGLE_CLIENT_SECRET`.

## 3. Definir quién puede entrar

En `.env.local` (y luego en Vercel):

```bash
ALLOWED_EMAIL_DOMAINS=fundacionvozpublica.cl
# opcional, para sumar cuentas sueltas que no calcen con los dominios de arriba
ALLOWED_EMAILS=
ALLOW_ALL=false
```

Ajusta el dominio al real de tu Workspace. La regla vive en `lib/auth.ts`
(función `signIn`) — es lo único que decide si alguien entra o no.

## 4. Desplegar en Vercel (gratis)

1. Sube este proyecto a un repo de GitHub propio (nuevo, separado de
   VisualLegislative).
2. En [vercel.com](https://vercel.com), **Add New → Project**, importa ese
   repo.
3. En **Settings → Environment Variables**, agrega todas las variables de
   `.env.example` con sus valores reales (`NEXTAUTH_URL` = la URL que te
   asigna Vercel, ej. `https://radiografia-sueldos.vercel.app`).
4. Vuelve a Google Cloud Console y agrega esa misma URL de producción a las
   "Authorized redirect URIs" (paso 4 de arriba).
5. Deploy. Listo — queda accesible solo para cuentas de los dominios que
   pusiste en `ALLOWED_EMAIL_DOMAINS`.

## Actualizar los datos del dashboard

Todo el contenido (gráficos, tablas, metodología) vive en
`public/dashboard.html` — es el mismo archivo autocontenido, se edita
directo ahí (no hay build step para ese archivo).
