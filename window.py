import pygame
from app_base import BaseApp
from typing import Tuple, Optional

from constants import TITLEBAR_HEIGHT, BORDER, FONT_SIZE


class Window:
    def __init__(
        self,
        id: int,
        app: BaseApp,
        rect: pygame.Rect,
        title: Optional[str] = None,
        embedded: bool = False,
    ) -> None:
        self.id = id
        self.app = app
        self.rect = rect
        self.title = title or getattr(app, "title", "App")

        self.dragging = False
        self.drag_offset = (0, 0)
        self.active = False
        self.visible = True
        self.embedded = embedded

        self.restore_pos = self.rect.topleft
        self.restore_size = self.rect.size
        self.maximized = False

        self.font = pygame.font.Font("fonts/TikTokSans.ttf", FONT_SIZE)
        if embedded:
            self.surface = pygame.Surface((rect.w - BORDER * 2, rect.h - BORDER * 2))
        else:
            self.surface = pygame.Surface(
                (rect.w - BORDER * 2, rect.h - TITLEBAR_HEIGHT - BORDER * 2)
            )

        self.btn_close_rect = pygame.Rect(
            0, 0, TITLEBAR_HEIGHT - BORDER, TITLEBAR_HEIGHT - BORDER
        )
        self.btn_max_rect = pygame.Rect(
            0, 0, TITLEBAR_HEIGHT - BORDER, TITLEBAR_HEIGHT - BORDER
        )
        self.btn_min_rect = pygame.Rect(
            0, 0, TITLEBAR_HEIGHT - BORDER, TITLEBAR_HEIGHT - BORDER
        )

    @property
    def titlebar_rect(self):
        if self.embedded:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.w, TITLEBAR_HEIGHT)

    @property
    def content_rect(self):
        if self.embedded:
            return pygame.Rect(
                self.rect.x + BORDER,
                self.rect.y + BORDER,
                self.rect.w - BORDER * 2,
                self.rect.h - BORDER,
            )
        return pygame.Rect(
            self.rect.x + BORDER,
            self.rect.y + TITLEBAR_HEIGHT,
            self.rect.w - BORDER * 2,
            self.rect.h - BORDER - TITLEBAR_HEIGHT,
        )

    def toggle_maximize(self):
        if getattr(self, "maximized", False):
            self.rect.size = self.restore_size
            self.rect.topleft = self.restore_pos
            self.maximized = False
        else:
            self.restore_pos = self.rect.topleft
            self.restore_size = self.rect.size
            self.rect.topleft = (0, 0)
            self.rect.size = (
                self.app.kernel.screen_width,
                self.app.kernel.screen_height,
            )
            self.maximized = True

    def contains_point(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        def move_and_fit(pos: Tuple[int, int]) -> None:
            x, y = pos
            ox, oy = self.drag_offset
            self.rect.x = x - ox
            self.rect.y = y - oy

            screen_w, screen_h = pygame.display.get_surface().get_size()
            self.rect.x = max(0, min(self.rect.x, screen_w - self.rect.w))
            self.rect.y = max(0, min(self.rect.y, screen_h - self.rect.h))

        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.titlebar_rect.collidepoint(event.pos):
                if self.btn_close_rect.collidepoint(event.pos):
                    self.app.kernel.close_window(self.id)
                    return True
                elif self.btn_max_rect.collidepoint(event.pos):
                    self.toggle_maximize()
                    return True
                elif self.btn_min_rect.collidepoint(event.pos):
                    self.visible = not self.visible
                    return True

                self.dragging = True
                if self.maximized:
                    self.toggle_maximize()
                    self.drag_offset = (
                        self.rect.w // 2,
                        TITLEBAR_HEIGHT // 2,
                    )
                    move_and_fit(event.pos)
                else:
                    self.drag_offset = (
                        event.pos[0] - self.rect.x,
                        event.pos[1] - self.rect.y,
                    )
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            move_and_fit(event.pos)
            return True
        try:
            self.app.handle_event(event)
        except Exception as e:
            print(f"[window] app.handle_event error in {self.id}: {e}")
        return False

    def update(self, dt: float) -> None:
        try:
            if self.surface.get_size() != (
                self.rect.w - BORDER * 2,
                self.rect.h - TITLEBAR_HEIGHT - BORDER,
            ):
                if self.embedded:
                    self.surface = pygame.Surface(
                        (self.rect.w - BORDER * 2, self.rect.h - BORDER * 2)
                    )
                else:
                    self.surface = pygame.Surface(
                        (
                            self.rect.w - BORDER * 2,
                            self.rect.h - TITLEBAR_HEIGHT - BORDER * 2,
                        )
                    )
            self.app.update(dt)
        except Exception as e:
            print(f"[window] app.update error in {self.id}: {e}")

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        if not self.embedded:
            # Title bar
            if not self.embedded:
                titlebar = self.titlebar_rect
                title_color = (50, 120, 200) if self.active else (100, 100, 100)
                pygame.draw.rect(surface, title_color, titlebar)

            # Title text
            title_surf = self.font.render(self.title, True, (255, 255, 255))
            title_x = self.rect.x + (self.rect.w - title_surf.get_width()) // 2
            title_y = self.rect.y + (TITLEBAR_HEIGHT - title_surf.get_height()) // 2
            surface.blit(title_surf, (title_x, title_y))

            # Buttons
            x = self.rect.right - (TITLEBAR_HEIGHT)
            y = self.rect.y + BORDER
            self.btn_close_rect.topleft = (x, y)

            x -= TITLEBAR_HEIGHT - BORDER
            self.btn_max_rect.topleft = (x, y)

            x -= TITLEBAR_HEIGHT - BORDER
            self.btn_min_rect.topleft = (x, y)

            pygame.draw.rect(surface, (200, 80, 80), self.btn_close_rect)
            pygame.draw.rect(surface, (200, 200, 80), self.btn_max_rect)
            pygame.draw.rect(surface, (80, 200, 80), self.btn_min_rect)

        try:
            self.app.draw(self.surface)
        except Exception as e:
            self.surface.fill((100, 0, 0))
            err = self.font.render(str(e), True, (255, 255, 255))
            self.surface.blit(err, (8, 8))

        # Border
        pygame.draw.rect(surface, (0, 0, 0), self.rect, BORDER)

        surface.blit(self.surface, self.content_rect)
