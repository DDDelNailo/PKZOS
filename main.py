import pygame
import argparse
from logger import Logger
from kernel import Kernel

from constants import SCREEN_SIZE, SCREEN_CAPTION, FPS, FLAGS


def main(app: str) -> None:
    Logger.log("main", "Pygame", "Initializing")
    pygame.init()
    Logger.log("main", "Pygame", f"Setting display mode to {SCREEN_SIZE}")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    Logger.log("main", "Pygame", f"Setting caption caption to {SCREEN_CAPTION}")
    pygame.display.set_caption(SCREEN_CAPTION)
    Logger.log("main", "Pygame", "Initializing clock")
    clock = pygame.time.Clock()
    Logger.log("main", "Pygame", "Disabling mixer")
    pygame.mixer.quit()

    Logger.log("main", "Kernel", "Initializing")
    kernel = Kernel(SCREEN_SIZE)
    Logger.kernel = kernel

    running = True

    embedded = kernel.launch_app(
        app, size=SCREEN_SIZE, pos=(0, 0), flags=FLAGS.EMBEDDED
    )
    if embedded is None:
        Logger.error("main", "Kernel", "Main embedded app did not launch")
        running = False

    if running:
        Logger.log("main", "Main", "Initializing event loop")
    while running:
        dt = clock.tick(FPS) / 1000.0

        if kernel.find_window_by_id(embedded) is None:
            Logger.log("main", "Kernel", "Embedded app closed")
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if len(kernel.windows) > 0 and kernel.windows[-1].active:
                    kernel.close_window(kernel.windows[-1].id)
                    continue
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    kernel.launch_app("counter", size=(400, 300), pos=(20, 20))
                elif event.key == pygame.K_F2:
                    kernel.launch_app(
                        "terminal", size=(800, 500), pos=(SCREEN_SIZE[0] - 800 - 20, 20)
                    )

            kernel.handle_event(event)

        kernel.update(dt)

        screen.fill((0, 0, 0))
        kernel.draw(screen)

        pygame.display.flip()

    Logger.log("main", "Kernel", "Stopping")
    Logger.log("main", "Kernel", "Closing all apps")
    for window in kernel.windows:
        kernel.close_window(window.id)

    Logger.log("main", "Pygame", "Quitting")
    pygame.quit()


if __name__ == "__main__":
    Logger.log("main", "Main", "PKZ Kernel 0.1")

    parser = argparse.ArgumentParser(description="A script that greets a user.")
    parser.add_argument(
        "--app", type=str, default="logger", help="The app to run on init."
    )

    args = parser.parse_args()

    main(args.app)
