import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";

// Importiere alle benötigten Komponenten von ShadCN/UI
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";

import { useFinderStore } from "@/store/findStore";

const CUISINE_OPTIONS = [
  { value: "italian", label: "Italienisch" },
  { value: "german", label: "Deutsch" },
  { value: "asian", label: "Asiatisch" },
  { value: "mexican", label: "Mexikanisch" },
  { value: "indian", label: "Indisch" },
];

const SETTING_OPTIONS = [
  { value: "any", label: "Egal" },
  { value: "cozy", label: "Gemütlich" },
  { value: "modern", label: "Modern" },
  { value: "romantic", label: "Romantisch" },
  { value: "outdoor", label: "Außenbereich" },
];


export function RestaurantFinder() {
  const {
    locationQuery,
    selectedCuisines,
    selectedSetting,
    weights,
    setLocationQuery,
    toggleCuisine,
    setSelectedSetting,
    setWeight,
    search,
  } = useFinderStore();
  
  const [openCombobox, setOpenCombobox] = React.useState(false);

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>Finde dein perfektes Restaurant</CardTitle>
        <CardDescription>
          Gib deine Wünsche an und wir finden den besten Ort für dich.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        <div className="grid gap-2">
          <Label htmlFor="location">Restaurant, Ort oder Stadt</Label>
          <Input 
            id="location" 
            placeholder="z.B. 'L'Osteria', 'Berlin' oder 'Musterstraße 1, Hamburg'" 
            value={locationQuery}
            onChange={(e) => setLocationQuery(e.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <Label>Küchenrichtung</Label>
           <Popover open={openCombobox} onOpenChange={setOpenCombobox}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={openCombobox}
                className="w-full justify-between font-normal"
              >
                {selectedCuisines.length > 0
                  ? selectedCuisines
                      .map(c => CUISINE_OPTIONS.find(o => o.value === c)?.label)
                      .join(", ")
                  : "Wähle eine oder mehrere Küchen..."}
                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
              <Command>
                <CommandInput placeholder="Suche Küchenrichtung..." />
                <CommandList>
                  <CommandEmpty>Nichts gefunden.</CommandEmpty>
                  <CommandGroup>
                    {CUISINE_OPTIONS.map((option) => (
                      <CommandItem
                        key={option.value}
                        value={option.label}
                        onSelect={() => {
                          toggleCuisine(option.value);
                        }}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            selectedCuisines.includes(option.value)
                              ? "opacity-100"
                              : "opacity-0"
                          )}
                        />
                        {option.label}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>

        <div className="grid gap-2">
            <Label htmlFor="setting">Ambiente</Label>
            <Select value={selectedSetting} onValueChange={setSelectedSetting}>
                <SelectTrigger id="setting">
                    <SelectValue placeholder="Wähle ein Ambiente" />
                </SelectTrigger>
                <SelectContent>
                    {SETTING_OPTIONS.map(option => (
                        <SelectItem key={option.value} value={option.value}>
                            {option.label}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>

        <div className="grid gap-4 pt-2">
            <Label>Wie wichtig sind dir die Kriterien?</Label>
            <div className="grid gap-2">
                <Label htmlFor="weight-cuisine" className="text-sm font-medium">Küchenrichtung</Label>
                <Slider 
                    id="weight-cuisine"
                    defaultValue={[weights.cuisine]} 
                    max={100} 
                    step={1}
                    onValueChange={(value) => setWeight('cuisine', value[0])}
                />
            </div>
             <div className="grid gap-2">
                <Label htmlFor="weight-setting" className="text-sm font-medium">Ambiente</Label>
                <Slider
                    id="weight-setting"
                    defaultValue={[weights.setting]}
                    max={100}
                    step={1}
                    onValueChange={(value) => setWeight('setting', value[0])}
                />
            </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" onClick={search} disabled={!locationQuery}>
            Suchen
        </Button>
      </CardFooter>
    </Card>
  );
}