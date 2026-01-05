// This file is the entry point for the React application.
// It sets up the root React component, wraps it with necessary providers (Clerk for auth, BrowserRouter for routing),
// and renders it into the DOM.

// Import StrictMode from React to enable additional checks and warnings in development
import { StrictMode } from 'react'
// Import createRoot from react-dom/client to create the root for rendering the app
import { createRoot } from 'react-dom/client'
// Import the global CSS styles
import './index.css'
// Import the main App component
import App from './App.jsx'
// Import BrowserRouter from react-router-dom to enable client-side routing
import { BrowserRouter } from 'react-router-dom'
// Import ClerkProvider from Clerk to provide authentication context to the app
import { ClerkProvider } from '@clerk/clerk-react'

// Create the root element by finding the DOM element with id 'root' and render the app into it
createRoot(document.getElementById('root')).render(
  // Wrap the app in StrictMode for development checks
  <StrictMode>
    {/* ClerkProvider wraps the app to provide authentication functionality */}
    <ClerkProvider
      publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY} // Public key for Clerk authentication, loaded from environment variables
      afterSignUpUrl="/farmer" // URL to redirect to after successful sign up
      afterSignInUrl="/farmer" // URL to redirect to after successful sign in
    >
      {/* BrowserRouter enables routing in the app */}
      <BrowserRouter>
        {/* Render the main App component */}
        <App />
      </BrowserRouter>
    </ClerkProvider>
  </StrictMode>
)
