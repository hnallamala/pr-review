import { Middlewares } from '..'

global['appConfig'] = require('../../../test/data/e2e/kpconfig/kpconfig.json')

describe('Middlewares', () => {
  let app: any

  beforeEach(() => {
    app = {
      use: jest.fn(),
      disable: jest.fn(),
    }
  })

  describe('use', () => {
    it('should use middlewares and disable x-powered-by', () => {
      Middlewares.use(app)

      expect(app.use).toHaveBeenCalled()
      expect(app.disable).toHaveBeenCalledWith('x-powered-by')
    })

    it('should handle x-guid header for api paths', () => {
      let capturedMiddleware: Function
      app.use.mockImplementation((middleware: Function) => {
        if (typeof middleware === 'function') {
          capturedMiddleware = middleware
        }
      })

      Middlewares.use(app)

      const xGuidMiddleware = app.use.mock.calls.find(
        (call) => typeof call[0] === 'function' && call[0].toString().includes('x-guid'),
      )[0]

      const req = {
        path: '/api/test',
        header: jest.fn().mockReturnValue('test-guid'),
      }
      const res = {
        set: jest.fn(),
      }
      const next = jest.fn()

      xGuidMiddleware(req, res, next)

      expect(req.header).toHaveBeenCalledWith('x-guid')
      expect(res.set).toHaveBeenCalledWith('X-response-guid', 'test-guid')
      expect(next).toHaveBeenCalled()
    })

    it('should not set x-guid header for non-api paths', () => {
      let capturedMiddleware: Function
      app.use.mockImplementation((middleware: Function) => {
        if (typeof middleware === 'function') {
          capturedMiddleware = middleware
        }
      })

      Middlewares.use(app)

      const xGuidMiddleware = app.use.mock.calls.find(
        (call) => typeof call[0] === 'function' && call[0].toString().includes('x-guid'),
      )[0]

      const req = {
        path: '/non-api/test',
        header: jest.fn().mockReturnValue('test-guid'),
      }
      const res = {
        set: jest.fn(),
      }
      const next = jest.fn()

      xGuidMiddleware(req, res, next)

      expect(res.set).not.toHaveBeenCalled()
      expect(next).toHaveBeenCalled()
    })

    it('should not set x-guid header when header is not present', () => {
      let capturedMiddleware: Function
      app.use.mockImplementation((middleware: Function) => {
        if (typeof middleware === 'function') {
          capturedMiddleware = middleware
        }
      })

      Middlewares.use(app)

      const xGuidMiddleware = app.use.mock.calls.find(
        (call) => typeof call[0] === 'function' && call[0].toString().includes('x-guid'),
      )[0]

      const req = {
        path: '/api/test',
        header: jest.fn().mockReturnValue(null),
      }
      const res = {
        set: jest.fn(),
      }
      const next = jest.fn()

      xGuidMiddleware(req, res, next)

      expect(res.set).not.toHaveBeenCalled()
      expect(next).toHaveBeenCalled()
    })
  })
})
