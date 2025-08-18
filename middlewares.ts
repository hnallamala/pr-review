import bodyParser from 'body-parser'
import cookieParser from 'cookie-parser'
import cors from 'cors'
import compression from 'compression'
import noCache from 'nocache'
import helmet from 'helmet'
import { Logger } from 'kp-nestjs-logger'
import { getLogger } from '../utilities/logger.util'

const oneYearInSeconds = 31536000

export class Middlewares {
  static use(app: any): void {
    const { logDebug } = getLogger(Logger, 'Middlewares', 'API_MIDDLEWARE')
    logDebug('initializing middlewares')

    app.use(bodyParser.urlencoded({ extended: true }))
    app.use(bodyParser.json())

    // Use CORS
    app.use(
      cors({
        origin: global['appConfig'].cors.origin,
        allowedHeaders: global['appConfig'].cors.allowedHeaders,
        methods: global['appConfig'].cors.methods,
        credentials: true,
        preflightContinue: false,
        optionsSuccessStatus: 204,
      }),
    )

    // Let's don the security helmet
    app.use(noCache())
    app.use(helmet({ contentSecurityPolicy: false, crossOriginEmbedderPolicy: false })) // graphql
    app.use(helmet.frameguard())
    app.use(helmet.hsts({ maxAge: oneYearInSeconds }))
    app.use(helmet.ieNoOpen())
    app.use(helmet.frameguard({ action: 'sameorigin' }))
    app.use(helmet.noSniff())
    app.use(helmet.referrerPolicy({ policy: 'same-origin' }))
    app.use(helmet.xssFilter())
    app.disable('x-powered-by')

    app.use(cookieParser())

    app.use((req, res, next) => {
      if (req.path.startsWith('/api')) {
        const xGuid = req.header('x-guid')
        if (xGuid) {
          res.set('X-response-guid', xGuid)
        }
      }

      next()
    })

    // Set up compression
    app.use(compression())

    logDebug('middlewares are set')
  }
}
