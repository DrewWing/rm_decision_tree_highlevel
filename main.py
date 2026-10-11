

# Some tests for decision trees for Sentry.

import logging

logger = logging.getLogger(__name__)

class State:
    def __init__(self, name:str):
        self.name=name

    def __repr__(self) -> str:
        return self.name


class SMachine:
    def __init__(self, lowHealthState:State, highHealthState:State, currentState:State|None = None, ):
        self.lowHealthState = lowHealthState
        self.highHealthState = highHealthState
        if (currentState == None): 
            self.currentState = self.lowHealthState
        else:
            self.currentState = currentState
        self.healthLimit = 25

    def __repr__(self) -> str:
        return f"StateMachine with current state {self.currentState}"

    def updateHealthState(self, health:float):
        if (health > self.healthLimit):
            self.currentState = self.highHealthState
        else:
            self.currentState = self.lowHealthState
        
        logger.info(f"[updateHealth] Updating state to {self.currentState} due to health at {health}  (limit at {self.healthLimit})")


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Program start")

    machine = SMachine(State("Low Health State"), State("High Health State"))

    while True:
        try:
            health = float(input("New health: "))
            machine.updateHealthState(health)

        except KeyboardInterrupt, EOFError:
            break


    logger.info("Program end")

if __name__ == '__main__':
    main()

