import pygame
import argparse
from logger import Logger
from kernel import Kernel

from constants import SCREEN_SIZE, SCREEN_CAPTION, FPS, FLAGS


def main(app: str) -> None:
    Logger.info("Initializing Pygame", "system")
    pygame.init()
    Logger.info(f"Display mode set to {SCREEN_SIZE}", "system")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    Logger.info(f"Window caption = '{SCREEN_CAPTION}'", "system")
    pygame.display.set_caption(SCREEN_CAPTION)
    clock = pygame.time.Clock()
    Logger.info("Initializing clock", "system")
    Logger.warn("Disabling pygame.mixer (audio disabled)", "system")
    pygame.mixer.quit()

    Logger.info("Initializing Kernel", "kernel")
    kernel = Kernel(SCREEN_SIZE)
    Logger.kernel = kernel
    Logger.info("Kernel successfully started", "kernel")

    running = True

    Logger.info(f"Launching main app '{app}' (embedded mode)", "kernel")
    embedded = kernel.launch_app(
        app, size=SCREEN_SIZE, pos=(0, 0), flags=FLAGS.EMBEDDED
    )

    if embedded is None:
        Logger.error(f"Failed to launch embedded app '{app}'", "kernel")
        running = False
    else:
        running = True

    if running:
        Logger.info("Starting event loop", "system")

    while running:
        dt = clock.tick(FPS) / 1000.0

        if kernel.find_window_by_id(embedded) is None:
            Logger.warn("Embedded app terminated by user", "kernel")
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Logger.warn("Quit request received", "system")
                if len(kernel.windows) > 0 and kernel.windows[-1].active:
                    Logger.debug(f"Closing topmost window", "kernel")
                    kernel.close_window(kernel.windows[-1].id)
                    continue
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    Logger.debug("Launching 'counter' via F1", "kernel")
                    kernel.launch_app("counter", size=(400, 300), pos=(20, 20))
                elif event.key == pygame.K_F2:
                    Logger.debug("Launching 'terminal' via F2", "kernel")
                    kernel.launch_app(
                        "terminal", size=(800, 500), pos=(SCREEN_SIZE[0] - 800 - 20, 20)
                    )

            kernel.handle_event(event)

        kernel.update(dt)

        screen.fill((0, 0, 0))
        kernel.draw(screen)

        pygame.display.flip()

    Logger.info("Stopping kernel", "kernel")
    Logger.info("Closing all apps", "kernel")

    for window in kernel.windows:
        Logger.info(f"Closing window {window.id}", "kernel")
        kernel.close_window(window.id)

    Logger.info("Shutting down Pygame", "system")
    pygame.quit()
    Logger.info("Shutdown complete", "system")


if __name__ == "__main__":
    Logger.info("PKZ Kernel v0.1 Starting", "system")

    parser = argparse.ArgumentParser(description="A script that greets a user.")
    parser.add_argument(
        "--app", type=str, default="logger", help="The app to run on init."
    )

    args = parser.parse_args()

    main(args.app)
