# Radiografía de Sueldos — acceso interno

Dashboard de remuneraciones del sector público chileno, protegido por login
institucional (Google **o** Microsoft) y restringido por dominio de correo.
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

## 3. Crear credenciales de Microsoft Entra ID (Azure AD)

1. Ve a [Azure Portal](https://portal.azure.com/) → **Microsoft Entra ID** →
   **App registrations → New registration**.
2. Nombre libre (ej. "Radiografía de Sueldos"). En "Redirect URI" elige tipo
   **Web** y pon:
   - `http://localhost:3000/api/auth/callback/azure-ad`
   - agrega también la de producción una vez que la tengas.
3. Copia el **Application (client) ID** → `AZURE_AD_CLIENT_ID`, y el
   **Directory (tenant) ID** → `AZURE_AD_TENANT_ID`.
4. **Certificates & secrets → New client secret** → copia el valor (no el ID)
   a `AZURE_AD_CLIENT_SECRET`.

## 4. Definir quién puede entrar

En `.env.local` (y luego en Vercel):

```bash
ALLOWED_EMAIL_DOMAINS=fundacionvozpublica.cl,fundacionvozpublica.onmicrosoft.com
# opcional, para sumar cuentas sueltas que no calcen con los dominios de arriba
ALLOWED_EMAILS=
ALLOW_ALL=false
```

Ajusta los dominios a los reales de tu Workspace/M365. La regla vive en
`lib/auth.ts` (función `signIn`) — es lo único que decide si alguien entra o
no, sin importar si usó Google o Microsoft para loguearse.

## 5. Desplegar en Vercel (gratis)

1. Sube este proyecto a un repo de GitHub propio (nuevo, separado de
   VisualLegislative).
2. En [vercel.com](https://vercel.com), **Add New → Project**, importa ese
   repo.
3. En **Settings → Environment Variables**, agrega todas las variables de
   `.env.example` con sus valores reales (`NEXTAUTH_URL` = la URL que te
   asigna Vercel, ej. `https://radiografia-sueldos.vercel.app`).
4. Vuelve a Google Cloud Console y Azure Portal y agrega esa misma URL de
   producción a las "Redirect URIs" (pasos 4 y 2 de arriba).
5. Deploy. Listo — queda accesible solo para cuentas de los dominios que
   pusiste en `ALLOWED_EMAIL_DOMAINS`.

## Actualizar los datos del dashboard

Todo el contenido (gráficos, tablas, metodología) vive en
`public/dashboard.html` — es el mismo archivo autocontenido, se edita
directo ahí (no hay build step para ese archivo).
