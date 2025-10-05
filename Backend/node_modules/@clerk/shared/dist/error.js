"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/error.ts
var error_exports = {};
__export(error_exports, {
  ClerkAPIResponseError: () => ClerkAPIResponseError,
  ClerkRuntimeError: () => ClerkRuntimeError,
  ClerkWebAuthnError: () => ClerkWebAuthnError,
  EmailLinkError: () => EmailLinkError,
  EmailLinkErrorCode: () => EmailLinkErrorCode,
  EmailLinkErrorCodeStatus: () => EmailLinkErrorCodeStatus,
  buildErrorThrower: () => buildErrorThrower,
  errorToJSON: () => errorToJSON,
  is4xxError: () => is4xxError,
  isCaptchaError: () => isCaptchaError,
  isClerkAPIResponseError: () => isClerkAPIResponseError,
  isClerkRuntimeError: () => isClerkRuntimeError,
  isEmailLinkError: () => isEmailLinkError,
  isKnownError: () => isKnownError,
  isMetamaskError: () => isMetamaskError,
  isNetworkError: () => isNetworkError,
  isPasswordPwnedError: () => isPasswordPwnedError,
  isReverificationCancelledError: () => isReverificationCancelledError,
  isUnauthorizedError: () => isUnauthorizedError,
  isUserLockedError: () => isUserLockedError,
  parseError: () => parseError,
  parseErrors: () => parseErrors
});
module.exports = __toCommonJS(error_exports);

// src/errors/parseError.ts
function parseErrors(data = []) {
  return data.length > 0 ? data.map(parseError) : [];
}
function parseError(error) {
  return {
    code: error.code,
    message: error.message,
    longMessage: error.long_message,
    meta: {
      paramName: error?.meta?.param_name,
      sessionId: error?.meta?.session_id,
      emailAddresses: error?.meta?.email_addresses,
      identifiers: error?.meta?.identifiers,
      zxcvbn: error?.meta?.zxcvbn,
      plan: error?.meta?.plan,
      isPlanUpgradePossible: error?.meta?.is_plan_upgrade_possible
    }
  };
}
function errorToJSON(error) {
  return {
    code: error?.code || "",
    message: error?.message || "",
    long_message: error?.longMessage,
    meta: {
      param_name: error?.meta?.paramName,
      session_id: error?.meta?.sessionId,
      email_addresses: error?.meta?.emailAddresses,
      identifiers: error?.meta?.identifiers,
      zxcvbn: error?.meta?.zxcvbn,
      plan: error?.meta?.plan,
      is_plan_upgrade_possible: error?.meta?.isPlanUpgradePossible
    }
  };
}

// src/errors/apiResponseError.ts
var ClerkAPIResponseError = class _ClerkAPIResponseError extends Error {
  clerkError;
  status;
  message;
  clerkTraceId;
  retryAfter;
  errors;
  constructor(message, { data, status, clerkTraceId, retryAfter }) {
    super(message);
    Object.setPrototypeOf(this, _ClerkAPIResponseError.prototype);
    this.status = status;
    this.message = message;
    this.clerkTraceId = clerkTraceId;
    this.retryAfter = retryAfter;
    this.clerkError = true;
    this.errors = parseErrors(data);
  }
  toString = () => {
    let message = `[${this.name}]
Message:${this.message}
Status:${this.status}
Serialized errors: ${this.errors.map(
      (e) => JSON.stringify(e)
    )}`;
    if (this.clerkTraceId) {
      message += `
Clerk Trace ID: ${this.clerkTraceId}`;
    }
    return message;
  };
};

// src/errors/errorThrower.ts
var DefaultMessages = Object.freeze({
  InvalidProxyUrlErrorMessage: `The proxyUrl passed to Clerk is invalid. The expected value for proxyUrl is an absolute URL or a relative path with a leading '/'. (key={{url}})`,
  InvalidPublishableKeyErrorMessage: `The publishableKey passed to Clerk is invalid. You can get your Publishable key at https://dashboard.clerk.com/last-active?path=api-keys. (key={{key}})`,
  MissingPublishableKeyErrorMessage: `Missing publishableKey. You can get your key at https://dashboard.clerk.com/last-active?path=api-keys.`,
  MissingSecretKeyErrorMessage: `Missing secretKey. You can get your key at https://dashboard.clerk.com/last-active?path=api-keys.`,
  MissingClerkProvider: `{{source}} can only be used within the <ClerkProvider /> component. Learn more: https://clerk.com/docs/components/clerk-provider`
});
function buildErrorThrower({ packageName, customMessages }) {
  let pkg = packageName;
  function buildMessage(rawMessage, replacements) {
    if (!replacements) {
      return `${pkg}: ${rawMessage}`;
    }
    let msg = rawMessage;
    const matches = rawMessage.matchAll(/{{([a-zA-Z0-9-_]+)}}/g);
    for (const match of matches) {
      const replacement = (replacements[match[1]] || "").toString();
      msg = msg.replace(`{{${match[1]}}}`, replacement);
    }
    return `${pkg}: ${msg}`;
  }
  const messages = {
    ...DefaultMessages,
    ...customMessages
  };
  return {
    setPackageName({ packageName: packageName2 }) {
      if (typeof packageName2 === "string") {
        pkg = packageName2;
      }
      return this;
    },
    setMessages({ customMessages: customMessages2 }) {
      Object.assign(messages, customMessages2 || {});
      return this;
    },
    throwInvalidPublishableKeyError(params) {
      throw new Error(buildMessage(messages.InvalidPublishableKeyErrorMessage, params));
    },
    throwInvalidProxyUrl(params) {
      throw new Error(buildMessage(messages.InvalidProxyUrlErrorMessage, params));
    },
    throwMissingPublishableKeyError() {
      throw new Error(buildMessage(messages.MissingPublishableKeyErrorMessage));
    },
    throwMissingSecretKeyError() {
      throw new Error(buildMessage(messages.MissingSecretKeyErrorMessage));
    },
    throwMissingClerkProviderError(params) {
      throw new Error(buildMessage(messages.MissingClerkProvider, params));
    },
    throw(message) {
      throw new Error(buildMessage(message));
    }
  };
}

// src/errors/emailLinkError.ts
var EmailLinkError = class _EmailLinkError extends Error {
  code;
  constructor(code) {
    super(code);
    this.code = code;
    this.name = "EmailLinkError";
    Object.setPrototypeOf(this, _EmailLinkError.prototype);
  }
};
var EmailLinkErrorCode = {
  Expired: "expired",
  Failed: "failed",
  ClientMismatch: "client_mismatch"
};
var EmailLinkErrorCodeStatus = {
  Expired: "expired",
  Failed: "failed",
  ClientMismatch: "client_mismatch"
};

// src/errors/runtimeError.ts
var ClerkRuntimeError = class _ClerkRuntimeError extends Error {
  clerkRuntimeError;
  /**
   * The error message in english, it contains a detailed description of the error.
   */
  message;
  /**
   * A unique code identifying the error, can be used for localization.
   */
  code;
  /**
   * The original error that was caught to throw an instance of ClerkRuntimeError.
   */
  cause;
  constructor(message, { code, cause }) {
    const prefix = "\u{1F512} Clerk:";
    const regex = new RegExp(prefix.replace(" ", "\\s*"), "i");
    const sanitized = message.replace(regex, "");
    const _message = `${prefix} ${sanitized.trim()}

(code="${code}")
`;
    super(_message);
    Object.setPrototypeOf(this, _ClerkRuntimeError.prototype);
    this.cause = cause;
    this.code = code;
    this.message = _message;
    this.clerkRuntimeError = true;
    this.name = "ClerkRuntimeError";
  }
  /**
   * Returns a string representation of the error.
   *
   * @returns A formatted string with the error name and message.
   */
  toString = () => {
    return `[${this.name}]
Message:${this.message}`;
  };
};

// src/errors/webAuthNError.ts
var ClerkWebAuthnError = class extends ClerkRuntimeError {
  /**
   * A unique code identifying the error, can be used for localization.
   */
  code;
  constructor(message, { code }) {
    super(message, { code });
    this.code = code;
  }
};

// src/errors/helpers.ts
function isUnauthorizedError(e) {
  const status = e?.status;
  const code = e?.errors?.[0]?.code;
  return code === "authentication_invalid" && status === 401;
}
function isCaptchaError(e) {
  return ["captcha_invalid", "captcha_not_enabled", "captcha_missing_token"].includes(e.errors[0].code);
}
function is4xxError(e) {
  const status = e?.status;
  return !!status && status >= 400 && status < 500;
}
function isNetworkError(e) {
  const message = (`${e.message}${e.name}` || "").toLowerCase().replace(/\s+/g, "");
  return message.includes("networkerror");
}
function isKnownError(error) {
  return isClerkAPIResponseError(error) || isMetamaskError(error) || isClerkRuntimeError(error);
}
function isClerkAPIResponseError(err) {
  return err && "clerkError" in err;
}
function isClerkRuntimeError(err) {
  return "clerkRuntimeError" in err;
}
function isReverificationCancelledError(err) {
  return isClerkRuntimeError(err) && err.code === "reverification_cancelled";
}
function isMetamaskError(err) {
  return "code" in err && [4001, 32602, 32603].includes(err.code) && "message" in err;
}
function isUserLockedError(err) {
  return isClerkAPIResponseError(err) && err.errors?.[0]?.code === "user_locked";
}
function isPasswordPwnedError(err) {
  return isClerkAPIResponseError(err) && err.errors?.[0]?.code === "form_password_pwned";
}
function isEmailLinkError(err) {
  return err.name === "EmailLinkError";
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ClerkAPIResponseError,
  ClerkRuntimeError,
  ClerkWebAuthnError,
  EmailLinkError,
  EmailLinkErrorCode,
  EmailLinkErrorCodeStatus,
  buildErrorThrower,
  errorToJSON,
  is4xxError,
  isCaptchaError,
  isClerkAPIResponseError,
  isClerkRuntimeError,
  isEmailLinkError,
  isKnownError,
  isMetamaskError,
  isNetworkError,
  isPasswordPwnedError,
  isReverificationCancelledError,
  isUnauthorizedError,
  isUserLockedError,
  parseError,
  parseErrors
});
//# sourceMappingURL=error.js.map