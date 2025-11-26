import pygame
from kernel import Kernel
from sample_app import SampleApp

SCREEN_SIZE = (1024, 640)
FPS = 60


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("PKZOS")
    clock = pygame.time.Clock()

    kernel = Kernel(SCREEN_SIZE)

    kernel.launch_app(SampleApp, title="Sample A", size=(360, 220), pos=(80, 80))
    kernel.launch_app(SampleApp, title="Sample B", size=(300, 180), pos=(220, 160))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            kernel.handle_event(event)

        kernel.update(dt)

        screen.fill((0, 0, 0))
        kernel.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
