import { Routes } from '@angular/router';
import { ChooseRole } from "./choose-role/choose-role";
import { GamePage } from "./game-page/game-page";
import { GetMapSize } from './get-map-size/get-map-size';

export const routes: Routes = [
    { path: '', redirectTo: 'choose-role', pathMatch: 'full' },
    { path: 'choose-role', component: ChooseRole },
    { path: 'get-map-size', component: GetMapSize },
    { path: 'game-page', component: GamePage },
    { path: '**', redirectTo: 'choose-role' },

];
